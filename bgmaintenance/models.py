from django.db import models
from django.utils import timezone
from django.views import generic
from django import forms
from django.core.validators import FileExtensionValidator

REPORT_TYPE_CHOICES = (
    ('LOCKED', 'Locked Out of Dorm'),
    ('PLUMBING', 'Plumbing'),
    ('WINDOW', 'Window'),
    ('ELECTRICAL', 'Electrical Issues'),
    ('FURNITURE', 'Broken Furniture'),
    ('APPLIANCES', 'Appliances'),
    ('SECURITY', 'Room Security (Broken Lock etc.)'),
    ('HVAC', 'HVAC'),
    ('INSECTS', 'Insects'),
    ('OTHER', 'Other (please describe)'),
)

STATUS_CHOICES = (
    ('Resolved', 'RESOLVED'),
    ('New', 'NEW'),
    ('In progress', 'IN PROGRESS')
)

BUILDING_CHOICES = (
    ('ALD', 'Alderman Library'),
    ('AQC', 'Aquatic and Fitness Center'),
    ('AST',	'Astronomy Building'),
    ('BGC',	'Birdwood Golf Course'),
    ('BOND', 'Bond House'),
    ('BMU',	'Bayly Building'),
    ('BRK',	'Brooks Hall'),
    ('BRN',	'Bryan Hall'),
    ('BRO',	'Brown College Library'),
    ('BRY',	'Bryant Hall'),
    ('CAB',	'New Cabell Hall'),
    ('CAM',	'Campbell Hall'),
    ('CAU',	'Cauthen House'),
    ('CDW',	'Clinical Department Wing'),
    ('CHE',	'Chemical Engineering Building'),
    ('CMN', 'Claude Moore Nursing'),
    ('COB',	'Cobb Hall'),
    ('COC',	'Cocke Hall'),
    ('CHM',	'Chemistry Building'),
    ('CLK',	'Clark Hall'),
    ('CLM',	'Clemons Library'),
    ('DR1',	"Dawson's Row Residence 1"),
    ('DRM',	'Drama Education Building'),
    ('DVS',	'Hospital West, Davis Wing'),
    ('FHL',	'Fayerweather Hall'),
    ('FRN',	'French House'),
    ('GIB',	'Gibson Hall'),
    ('GIL',	'Gilmer Hall'),
    ('GSB',	'Darden School'),
    ('HAL',	'Halsey Hall'),
    ('HOD',	'Hotel D, East Range'),
    ('HOM',	'Home of the Instructor'),
    ('HSBB', 'Hunter Smith Band Building'),
    ('ICE',	'Charlottesville Ice Park'),
    ('JAG',	'Judge Advocate General School'),
    ('JOR',	'Jordan Hall'),
    ('JSR',	'Jesser Hall'),
    ('KER',	'Kerchof Hall'),
    ('LACY', 'Lacy Hall'),
    ('LEV',	'Levering Hall'),
    ('LHO',	'Lambeth House'),
    ('LPJ',	'Luther P. Jackson House'),
    ('LWO',	'Lower West Oval Room, Rotunda'),
    ('MCL',	'McLeod Hall'),
    ('MEC',	'Mechanical Engineering Building'),
    ('MED',	'Old Medical School'),
    ('MGM',	'Memorial Gymnasium'),
    ('MHP',	'Multistory Building (Old Hospital)'),
    ('MH3',	'Monroe Hill Range'),
    ('MIN',	'Minor Hall'),
    ('MON',	'Monroe Hall'),
    ('MSB',	'Materials Science Building'),
    ('MUN',	'Mary Munford House'),
    ('NAU',	'Nau Hall'),
    ('NHL',	'Newcomb Hall'),
    ('OBS',	'McCormick Observatory'),
    ('OCH',	'Old Cabell Hall'),
    ('OLS',	'Olsson Hall'),
    ('PBY',	'Peabody Hall'),
    ('PHS',	'Physics Building'),
    ('PV5',	'Pavilion V'),
    ('PV8',	'Pavilion VIII'),
    ('RAN',	'Randall Hall'),
    ('RAO',	'National Radio Astronomy Observatory'),
    ('RBT',	'Robertson Hall'),
    ('RDL',	'Ridley Hall (previously known as RFN Ruffner)'),
    ('REA',	'Nuclear Reactor'),
    ('REC',	'Slaughter Recreation Center'),
    ('RICE', 'Rice Hall'),
    ('RSH',	'Rouss Hall'),
    ('RTN',	'Rotunda'),
    ('RUF',	'Ruffin Hall'),
    ('SHH',	'Shea House'),
    ('SHN',	'Shannon House'),
    ('SHW',	'Student Health and Wellness'),
    ('SLH',	'Slaughter Hall'),
    ('STB',	'Barracks Stables'),
    ('STC',	'Stacey Hall'),
    ('THN',	'Thornton Hall'),
    ('WIL',	'Wilson Hall'),
    ('WNR',	'Warner Hall'),
    ('WSB',	'Withers-Brown Hall'),
    ('ZMA',	'Zehmer Hall Annex'),
    ('ZMR',	'Zehmer Hall')
)


class Report(models.Model):
    userReporting = models.CharField(max_length=50)
    pub_date = models.DateTimeField(auto_now_add=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(max_length=200)
    status = models.CharField(max_length=20, default='New')
    building = models.CharField(max_length=50, choices=BUILDING_CHOICES, blank=True)  # Allow blank
    area = models.CharField(max_length=200, blank=True)  # Allow blank

class Comment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    username = models.CharField(max_length=50)

    comment_text = models.CharField(max_length=200)


class File(models.Model):
    # Foreign key for Report
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    # File field for storing the file on Amazon S3
    file = models.FileField()
    # file_name = models.CharField(max_length=60)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['userReporting', 'report_type', 'description', 'building', 'area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['userReporting'].widget.attrs['readonly'] = True

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)