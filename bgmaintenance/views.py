import boto3
import pytz
from botocore.exceptions import ClientError
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
import base64
from django.contrib.sites.shortcuts import get_current_site

from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from django.contrib.auth import login

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

import requests

import mysite
from .models import ReportForm, REPORT_TYPE_CHOICES, Report, CommentForm, Comment, FileForm, BUILDING_CHOICES


def home(request):

    domain = request.get_host()

    if '127' in domain or 'local' in domain:
        redirect_uri = f'http://{domain}'
    else:
        redirect_uri = f'https://{domain}'

    return render(request, "bgmaintenance/home.html", {'domain': redirect_uri, 'header_image': getStaticImage('uva_logo.jpg'),
                                                       'sabrepic': getStaticImage('UVASabreLogo.png'),'mccorm': getStaticImage('mccorm.jpg'), 'building': getStaticImage('uva_building.jpg'),
                                                       'dormroom': getStaticImage('uva_dormroom.jpg'), 'overlaypic': getStaticImage('overlay.jpg'),
                                                        'rotundapic': getStaticImage('rotunda.jpg'), 'jackpic': getStaticImage('JackChellman.jpg'),
                                                       'alderman': getStaticImage('AldermanDormBarling.jpg')})


def logout_view(request, report_id=1):
    logout(request)
    return redirect("/")

def getStaticImage(file_name: str):
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=mysite.settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=mysite.settings.AWS_SECRET_ACCESS_KEY)
        bucket_name = mysite.settings.AWS_STORAGE_BUCKET_NAME

        try:
            file_object = s3.get_object(Bucket=bucket_name, Key='static/' + file_name)
            file_content = file_object['Body'].read()

            encoded_content = file_content

            content_type = file_object['ContentType']
            if content_type == 'image/jpeg' or content_type == 'image/png':
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            return {'name': file_name, 'content': encoded_content, 'content_type': content_type}
        except ClientError as e:
            # Handle error fetching file content or metadata
            print(f"Error fetching file '{file_name}': {e}")


    except ClientError as e:
        # Handle error listing objects (e.g., bucket not found)
        error_message = f"Error listing objects in bucket '{bucket_name}': {e}"
        return render(request, 'bgmaintenance/home.html')
    except ImproperlyConfigured as e:
        # Handle improperly configured settings
        error_message = f"Error with Django settings: {e}"
        return render(request, 'bgmaintenance/home.html')



def report_success(request):
    return render(request, "bgmaintenance/report_success.html", {'header_image': getStaticImage('uva_logo.jpg'),
    'sabrepic': getStaticImage('UVASabreLogo.png')})

def submit_anonymous_report(request):
    return submit_report(request, True)


def submit_report(request, anonymousUser=False):
    wrongFile = False
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.status = 'New'
            if request.FILES.get('file'):
                my_file = request.FILES['file']
                if '.jpg' in my_file.name or '.jpeg' in my_file.name or '.pdf' in my_file.name or '.txt' in my_file.name:
                    report.save()
                    uploadFile(request, report.id)
                    return redirect('report_success')
                else:
                    wrongFile = True
            else:
                report.save()
                return redirect('report_success')
    else:
        form = ReportForm()

    return render(request, 'bgmaintenance/reportu.html', {'form': form,
                                                          'REPORT_TYPE_CHOICES': REPORT_TYPE_CHOICES,
                                                          'wrongFile': wrongFile, 'anonymousUser': anonymousUser,
                                                          'BUILDING_CHOICES' : BUILDING_CHOICES,
                                                          'header_image': getStaticImage('uva_logo.jpg'),
                                                          'sabrepic': getStaticImage('UVASabreLogo.png')})

def uploadFile(request, report_id):
    my_file = request.FILES['file']
    uploaded_file = ContentFile(my_file.read())

    s3 = boto3.client('s3',
                      aws_access_key_id=mysite.settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=mysite.settings.AWS_SECRET_ACCESS_KEY)

    bucket_name = mysite.settings.AWS_STORAGE_BUCKET_NAME
    content_type = my_file.content_type

    upload_location_key = f"{report_id}/{my_file.name}"
    s3.upload_fileobj(uploaded_file, bucket_name, upload_location_key, ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'})

def view_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if report.status == 'New' and request.user.is_superuser:
        report.status = 'In Progress'
        report.save()
        new_comment = Comment.objects.create(report=report, username=request.user.username, comment_text=f'Marked as "In Progress" by {request.user.username}')
        new_comment.save()

    if request.method == 'POST' and 'mark_resolved' in request.POST:
        report.status = 'Resolved'
        report.save()
        new_comment = Comment.objects.create(report=report, username=request.user.username, comment_text=f'Marked as "Resolved" by {request.user.username}')
        new_comment.save()
        return redirect('view_report', report_id=report_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.username = request.user.username
            comment.report = report
            comment.save()
            return redirect('view_report', report_id=report_id)
        else:
            if request.method == 'POST' and request.FILES.get('file'):
                form = FileForm(request.POST, request.FILES)
                if form.is_valid():

                    my_file = request.FILES['file']
                    uploaded_file = ContentFile(my_file.read())

                    file = form.save(commit=False)
                    file.report = report
                    file.save()


                    s3 = boto3.client('s3',
                                      aws_access_key_id=mysite.settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=mysite.settings.AWS_SECRET_ACCESS_KEY)

                    bucket_name = mysite.settings.AWS_STORAGE_BUCKET_NAME
                    content_type = my_file.content_type

                    upload_location_key = f"{report_id}/{my_file.name}"
                    s3.upload_fileobj(uploaded_file, bucket_name, upload_location_key, ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'})




                    return redirect('view_report', report_id=report_id)

            else:
                form = FileForm()

    else:
        form = CommentForm()

    comments_list = Comment.objects.filter(report_id=report_id)


    files = []

    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=mysite.settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=mysite.settings.AWS_SECRET_ACCESS_KEY)
        bucket_name = mysite.settings.AWS_STORAGE_BUCKET_NAME

        # List objects in the bucket with a specific prefix corresponding to the report_id
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{report_id}/")

        if 'Contents' in response:
            for obj in response['Contents']:
                # Extract file name from object key
                file_name = obj['Key']

                # Fetch file content
                try:
                    file_object = s3.get_object(Bucket=bucket_name, Key=file_name)
                    file_content = file_object['Body'].read()

                    encoded_content = file_content

                    # Fetch content type for the object
                    content_type = file_object['ContentType']
                    if content_type == 'image/jpeg':
                        encoded_content = base64.b64encode(file_content).decode('utf-8')

                    # Add file info to the list
                    files.append({'name': file_name, 'content': encoded_content, 'content_type': content_type})
                except ClientError as e:
                    # Handle error fetching file content or metadata
                    print(f"Error fetching file '{file_name}': {e}")

    except ClientError as e:
        # Handle error listing objects (e.g., bucket not found)
        error_message = f"Error listing objects in bucket '{bucket_name}': {e}"
        return render(request, 'bgmaintenance/home.html')
    except ImproperlyConfigured as e:
        # Handle improperly configured settings
        error_message = f"Error with Django settings: {e}"
        return render(request, 'bgmaintenance/home.html')

    firstImageFile = 0
    for file in files:
        if 'jpg' in file['name']:
            firstImageFile = file
            break
        elif 'jpeg' in file['name']:
            firstImageFile = file
            break

    return render(request, "bgmaintenance/view_report.html", {'form': form, 'report': report,
                                                              'comments_list': comments_list, 'files': files,
                                                              'firstImageFile': firstImageFile,
                                                              'header_image': getStaticImage('uva_logo.jpg'),
                                                              'sabrepic': getStaticImage('UVASabreLogo.png')})


def report_list(request):
    # Sorting parameter from the GET request
    sort_by = request.GET.get('sort', None)

    # Filter reports based on user type
    if request.user.is_superuser:
        allReports = Report.objects.all()
    else:
        allReports = Report.objects.filter(userReporting=request.user.username)

    # Apply sorting based on the 'sort' GET parameter
    if sort_by == 'date':
        allReports = allReports.order_by('-pub_date')  # Change '-' to '' for ascending order
    elif sort_by == 'report_id':
        allReports = allReports.order_by('id')
    elif sort_by == 'report_type':
        allReports = allReports.order_by('report_type')
    elif sort_by == 'building':
        allReports = allReports.order_by('building')
    elif sort_by == 'email':
        allReports = allReports.order_by('userReporting')
    elif sort_by == 'status':
        newReports = allReports.filter(status='New')
        activeReports = allReports.filter(status='In Progress')
        oldReports = allReports.filter(status='Resolved')

        allReports = list(newReports) + list(activeReports) + list(oldReports)

    # Default sorting or no sorting clicked, categorize by status as before
    if not sort_by:
        newReports = allReports.filter(status='New')
        activeReports = allReports.filter(status='In Progress')
        oldReports = allReports.filter(status='Resolved')

        allReports = list(newReports) + list(activeReports) + list(oldReports)

    return render(request, 'bgmaintenance/report_list.html', {
        'allreports': allReports,
        'sortedMethod': sort_by or 'Status',  # Default to 'Status' if no sort parameter
        'header_image': getStaticImage('uva_logo.jpg'),
        'sabrepic': getStaticImage('UVASabreLogo.png')
    })


def google_callback(request):
    auth_code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_endpoint = 'https://oauth2.googleapis.com/token'

    # current_site = get_current_site(request)
    # domain = current_site.domain
    domain = request.get_host()

    if '127' in domain or 'local' in domain:
        redirect_uri = f'http://{domain}/accounts/google/login/callback/'
    else:
        redirect_uri = f'https://{domain}/accounts/google/login/callback/'

    token_data = {
        'code': auth_code,
        'client_id': '251991578412-s87j9geg1f3jn9nqjvjgn4f1rs9qd2hb.apps.googleusercontent.com',
        'client_secret': mysite.settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_endpoint, data=token_data)
    token_response = response.json()

    # Extract the access token from the token response
    access_token = token_response.get('access_token')

    # Fetch user information from Google's userinfo endpoint
    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    userinfo_response = requests.get(userinfo_endpoint, headers=headers)
    userinfo_data = userinfo_response.json()

    user_email = userinfo_data.get('email')
    user_fn = userinfo_data.get('given_name')
    user_ln = userinfo_data.get('family_name')

    user, created = User.objects.get_or_create(first_name=user_fn, last_name=user_ln, username=user_email, email=user_email)

    user.backend = f'{ModelBackend.__module__}.{ModelBackend.__qualname__}'

    # Log the user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # You may want to redirect the user to another page after authentication
    return redirect('home')