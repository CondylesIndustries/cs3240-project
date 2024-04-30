from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bgmaintenance.models import Report,Comment, ReportForm
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from bgmaintenance.models import Report, File
from django.urls import reverse

#Create your tests here.

class Test1(TestCase):

    def test_1(self):
        report = Report.objects.create(userReporting='admin')
        self.assertEqual(report.userReporting, 'admin')
    def test_2(self):
        report = Report.objects.create(description="here's my description")
        self.assertEqual(report.description, "here's my description")


class TestReportModel(TestCase):

    def test_create_report_with_all_fields(self):
        user = User.objects.create(username='testuser', password='testpass')
        report = Report.objects.create(
            userReporting=user.username,
            description='Light bulb out in hallway',
            pub_date=timezone.now(),
            report_type='ELECTRICAL',
            status='New',
            building='MAIN',
            area='First floor'
        )
        self.assertEqual(report.userReporting, user.username)
        self.assertEqual(report.description, 'Light bulb out in hallway')
        self.assertEqual(report.report_type, 'ELECTRICAL')
        self.assertEqual(report.status, 'New')
        self.assertEqual(report.building, 'MAIN')
        self.assertEqual(report.area, 'First floor')

    def test_report_status_update(self):
        report = Report.objects.create(description="Flickering light in lab", status='New')
        report.status = 'Resolved'
        report.save()
        self.assertEqual(Report.objects.get(id=report.id).status, 'Resolved')

    def test_comment_creation(self):
        report = Report.objects.create(description="Leaky faucet in bathroom", status='New')
        comment = Comment.objects.create(report=report, comment_text="Repair scheduled", username="maintenance_staff")
        self.assertTrue(Comment.objects.filter(report=report).exists())
        self.assertEqual(comment.comment_text, "Repair scheduled")
        self.assertEqual(comment.username, "maintenance_staff")

    def test_report_query_by_building(self):
        Report.objects.create(description="Overflowing trash can", building='LIBRARY')
        Report.objects.create(description="Broken window", building='GYM')
        library_reports = Report.objects.filter(building='LIBRARY')
        self.assertEqual(library_reports.count(), 1)
        self.assertEqual(library_reports.first().description, "Overflowing trash can")

    def test_report_deletion(self):
        report = Report.objects.create(description="Graffiti on wall")
        report_id = report.id
        report.delete()
        self.assertFalse(Report.objects.filter(id=report_id).exists())

    def test_report_form_save(self):
        form_data = {
            'userReporting': 'admin',
            'description': 'AC not working',
            'report_type': 'HVAC',
            'building': 'SCIENCE',
            'area': 'Second floor'
        }
        form = ReportForm(data=form_data)
        if form.is_valid():
            report = form.save()
            self.assertTrue(Report.objects.filter(description='AC not working').exists())
            self.assertEqual(report.building, 'SCIENCE')

    def test_report_form_validity(self):
        form_data = {
            'userReporting': 'admin',
            'description': 'Broken projector in classroom',
            'report_type': 'ELECTRICAL',
            'building': 'ALD',
            'area': 'Room 101'
        }
        form = ReportForm(data=form_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())


class FileUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.report = Report.objects.create(
            userReporting=self.user.username,
            description="Test report",
            report_type="SECURITY",
            building="ALD"
        )

    def test_file_upload(self):
        file_content = b'This is a test file.'
        uploaded_file = SimpleUploadedFile("testfile.txt", file_content, content_type="text/plain")

        file_instance = File.objects.create(report=self.report, file=uploaded_file)

        saved_file = File.objects.get(id=file_instance.id)

        self.assertTrue(saved_file.file)
        self.assertIn('testfile.txt', saved_file.file.name)

        saved_file.file.delete(save=False)


    def tearDown(self):
        File.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()


class ReportStatusChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.report = Report.objects.create(
            userReporting=self.user.username,
            description="Light bulb needs replacement",
            report_type="ELECTRICAL",
            building="ALD",
            status="New"
        )

    def test_change_status_to_resolved(self):
        self.report.status = 'Resolved'
        self.report.save()

        updated_report = Report.objects.get(id=self.report.id)

        self.assertEqual(updated_report.status, 'Resolved')

    def tearDown(self):
        Report.objects.all().delete()
        User.objects.all().delete()


class ReportingTest(unittest.TestCase):
    def setUp(self):
        chrome_service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        options = [
            "--headless",
            "--disable-gpu",
            "--window-size=1920,1200",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
        for option in options:
            chrome_options.add_argument(option)

        self.selenium = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.selenium.implicitly_wait(10)

    def tearDown(self):
        self.selenium.quit()

    def test_home_page_navigation(self):
        self.selenium.get("https://cs3240-project-a-30-e059aad2cf6b.herokuapp.com/")

        self.assertIn("Facilities Management", self.selenium.title)

        self.assertEqual(self.selenium.current_url, "https://cs3240-project-a-30-e059aad2cf6b.herokuapp.com/")

    def test_anonymous_report_redirection(self):
        self.selenium.get("https://cs3240-project-a-30-e059aad2cf6b.herokuapp.com/")

        WebDriverWait(self.selenium, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Anonymous Reporting"))
        ).click()

        WebDriverWait(self.selenium, 20).until(
            EC.url_to_be("https://cs3240-project-a-30-e059aad2cf6b.herokuapp.com/reporta")
        )

    def test_username_field_is_anonymous(self):
        self.selenium.get("https://cs3240-project-a-30-e059aad2cf6b.herokuapp.com/")

        anonymous_reporting_btn = WebDriverWait(self.selenium, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Anonymous Reporting"))
        )
        anonymous_reporting_btn.click()

        WebDriverWait(self.selenium, 20).until(
            EC.presence_of_element_located((By.ID, "userReporting"))
        )

        username_field_value = self.selenium.find_element(By.ID, "userReporting").get_attribute("value")
        self.assertEqual(username_field_value, "Anonymous")

if __name__ == "__main__":
    unittest.main()