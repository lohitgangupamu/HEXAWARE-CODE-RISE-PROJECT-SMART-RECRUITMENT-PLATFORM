
# users/models.py

from django.db import models

class JobPosting(models.Model):
    JOB_DEPARTMENTS = [
        ('HR', 'HR'),
        ('IT', 'IT'),
        ('Marketing', 'Marketing'),
        ('Sales', 'Sales'),
    ]
    
    EMPLOYMENT_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]

   

    title = models.CharField(max_length=200)
    description = models.TextField()
    department = models.ForeignKey(
        'JobCategory',
        on_delete=models.CASCADE,
        limit_choices_to={'category_type': 'Department'},
        related_name='job_postings_department'
    )
    location = models.ForeignKey(
        'JobCategory',
        on_delete=models.CASCADE,
        limit_choices_to={'category_type': 'Location'},
        related_name='job_postings_location'
    )
    employment_type = models.ForeignKey(
        'JobCategory',
        on_delete=models.CASCADE,
        limit_choices_to={'category_type': 'EmploymentType'},
        related_name='job_postings_employment_type'
    )
    salary_range = models.CharField(max_length=100)
    application_deadline = models.DateField()
    required_qualifications = models.TextField()
    preferred_qualifications = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    


  # Update to match the model field


from django.db import models

class JobCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('Department', 'Department'),
        ('Location', 'Location'),
        ('EmploymentType', 'Employment Type')
    ]

    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPE_CHOICES)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

# users/models.py

from django.db import models

class ApplicationForm(models.Model):
    name = models.CharField(max_length=200)
    associated_job = models.ForeignKey('JobPosting', on_delete=models.CASCADE)
    form_fields = models.JSONField()  # To store customizable fields in JSON format

    def __str__(self):
        return self.name

from django.db import models

# users/models.py

from django.db import models

class Application(models.Model):
    applicant_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    date_applied = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.applicant_name

# users/models.py

from django.db import models

class Notification(models.Model):
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message

# users/models.py

from django.db import models

class Applicant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')

class Interview(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    status = models.CharField(max_length=50, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.applicant_name} - {self.job_title}"

class StatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    date_changed = models.DateTimeField(auto_now_add=True)


# users/models.py

# users/models.py

from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    name = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    filters = models.JSONField()  # Assuming this stores the filter criteria
    fields = models.JSONField()  # Assuming this stores the fields to include
    criteria = models.JSONField()  # New field to store additional criteria

    def __str__(self):
        return self.name

# Create your models here.


