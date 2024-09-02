# job_portal/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username or email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    remember_me = forms.BooleanField(
        label="Remember Me",
        required=False
    )
# users/forms.py

class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your registered email'})
    )

    # users/forms.py



class PasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        min_length=8,
        required=True,
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        min_length=8,
        required=True,
    )
# users/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        strip=False,
        min_length=8,
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
        strip=False,
        min_length=8,
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

# users/forms.py
# forms.py
from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'title', 'description', 'department', 'location', 'employment_type',
            'salary_range', 'application_deadline', 'required_qualifications',
            'preferred_qualifications', 'responsibilities'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Enter the job description'}),
            'required_qualifications': forms.Textarea(attrs={'placeholder': 'Enter the required qualifications'}),
            'preferred_qualifications': forms.Textarea(attrs={'placeholder': 'Enter the preferred qualifications'}),
            'responsibilities': forms.Textarea(attrs={'placeholder': 'Enter the job responsibilities'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

# forms.py
from django import forms
from .models import JobCategory

class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = ['category_type', 'category_name']
        widgets = {
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }

# users/forms.py


# users/forms.py

from django import forms
from .models import ApplicationForm, JobPosting, Applicant

class ApplicationFormForm(forms.ModelForm):
    class Meta:
        model = ApplicationForm
        fields = ['name', 'associated_job', 'form_fields']
        widgets = {
            'form_fields': forms.HiddenInput(),  # Hidden field to store JSON data
        }

# forms.py
# users/forms.py

from django import forms
from .models import Interview

class RescheduleInterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interview_date', 'interview_time']
        widgets = {
            'interview_date': forms.DateInput(attrs={'type': 'date'}),
            'interview_time': forms.TimeInput(attrs={'type': 'time'}),
        }


# forms.py
 # Ensure these models are defined

# users/forms.py
# users/forms.py
from django import forms
from .models import Interview, Applicant, JobPosting

class ScheduleInterviewForm(forms.ModelForm):
    interview_mode_choices = [
        ('', 'Select interview mode'),  # Default empty choice
        ('In-Person', 'In-Person'),
        ('Video Call', 'Video Call'),
        ('Phone Call', 'Phone Call'),
        ('Teams Call', 'Teams Call'),
    ]
    
    applicant = forms.ModelChoiceField(
        queryset=Applicant.objects.all(),
        label="Applicant Name"
    )
    
    job_posting = forms.ModelChoiceField(
        queryset=JobPosting.objects.all(),
        label="Job Title"
    )
    
    interview_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Interview Date"
    )
    
    interview_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Interview Time"
    )
    
    interviewers = forms.ModelMultipleChoiceField(
        queryset=Applicant.objects.all(),  # Adjust if interviewers are a different model
        widget=forms.CheckboxSelectMultiple,
        label="Interviewers"
    )
    
    interview_mode = forms.ChoiceField(
        choices=interview_mode_choices,
        label="Interview Mode"
    )
    
    interview_location = forms.CharField(
        required=False,
        label="Interview Location",
        widget=forms.TextInput(attrs={'placeholder': 'Enter interview location'})
    )

    class Meta:
        model = Interview
        fields = ['applicant', 'job_posting', 'interview_date', 'interview_time', 'interviewers', 'interview_mode', 'interview_location']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the form field visibility based on interview mode
        if 'interview_mode' in self.data:
            if self.data.get('interview_mode') == 'In-Person':
                self.fields['interview_location'].required = True
            else:
                self.fields['interview_location'].required = False
        elif self.instance and self.instance.interview_mode == 'In-Person':
            self.fields['interview_location'].required = True

    def clean(self):
        cleaned_data = super().clean()
        interview_mode = cleaned_data.get('interview_mode')
        interview_location = cleaned_data.get('interview_location')

        if interview_mode == 'In-Person' and not interview_location:
            self.add_error('interview_location', 'This field is required when Interview Mode is In-Person.')

        return cleaned_data

# users/forms.py
# users/forms.py

# users/forms.py

from django import forms

class UpdateStatusForm(forms.Form):
    current_status = forms.CharField(
        label="Current Status",
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    new_status = forms.ChoiceField(
        label="New Status",
        choices=[
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('hired', 'Hired'),
            ('rejected', 'Rejected')
        ],
        widget=forms.Select(attrs={'placeholder': 'Select new status'})
    )
    notes = forms.CharField(
        label="Notes",
        widget=forms.Textarea(attrs={'placeholder': 'Enter any notes'}),
        required=False
    )


# users/forms.py

from django import forms

class ComposeMessageForm(forms.Form):
    recipient = forms.EmailField(
        label="Recipient Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter recipient email'})
    )
    subject = forms.CharField(
        label="Subject",
        widget=forms.TextInput(attrs={'placeholder': 'Enter subject'})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'placeholder': 'Enter your message'})
    )

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

# users/forms.py

from django import forms
from .models import Report

class CreateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['name','criteria']  # Only include fields that are actually in the Report model

    # Additional fields not part of the model
    date_range = forms.DateField(
        label="Date Range",
        widget=forms.DateInput(attrs={'placeholder': 'Select date range'}),
        required=True
    )
    status = forms.ChoiceField(
        label="Application Status",
        choices=[('', 'Select status'), ('new', 'New'), ('in_progress', 'In Progress'), ('hired', 'Hired'), ('rejected', 'Rejected')],
        required=False
    )
    position = forms.ChoiceField(
        label="Position",
        choices=[('', 'Select position'), ('developer', 'Developer'), ('designer', 'Designer'), ('manager', 'Manager')],
        required=False
    )
    source = forms.ChoiceField(
        label="Source",
        choices=[('', 'Select source'), ('job_board', 'Job Board'), ('referral', 'Referral')],
        required=False
    )
    fields_to_include = forms.MultipleChoiceField(
        label="Fields to Include",
        choices=[('applicant_name', 'Applicant Name'), ('date_applied', 'Date Applied'), ('status', 'Status'), ('source', 'Source')],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

