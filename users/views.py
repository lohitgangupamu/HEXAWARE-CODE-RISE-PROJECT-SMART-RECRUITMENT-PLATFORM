
# job_portal/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from .forms import LoginForm, PasswordRecoveryForm, CustomUserCreationForm, JobPostingForm, JobCategoryForm
from .models import JobPosting, JobCategory


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(1209600)  # 2 weeks
                return redirect('dashboard')  # Redirect to your dashboard view
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

def password_recovery(request):
    if request.method == 'POST':
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user_model = get_user_model()
            try:
                user = user_model.objects.get(email=email)
                token_generator = default_token_generator
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                site = get_current_site(request)
                reset_link = f"http://{site.domain}/users/password_reset_confirm/{uid}/{token}/"
                subject = "Password Reset Request"
                message = render_to_string('users/password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                    'site_name': site.name,
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                return render(request, 'users/password_recovery_done.html')
            except user_model.DoesNotExist:
                form.add_error(None, 'No account found with this email address.')
    else:
        form = PasswordRecoveryForm()
    return render(request, 'users/password_recovery.html', {'form': form})

# Create your views here.

# users/views.py
# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                email_template_name='users/password_reset_email.html',
                subject_template_name='users/password_reset_subject.txt',
                request=request,
                use_https=request.is_secure(),
                from_email=None,
            )
            messages.success(request, 'Password reset email has been sent.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'users/password_reset.html', {'form': form})




from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login

User = get_user_model()

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password has been reset successfully.')
                return redirect('login')
        else:
            form = PasswordResetForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid.')
        return redirect('login')

# users/views.py

# users/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def home(request):
    return redirect('login') 

# users/views.py


from django.shortcuts import render, redirect
from .forms import JobPostingForm


def create_job(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')  # Ensure you have a URL pattern named 'job_list'
    else:
        form = JobPostingForm()
    return render(request, 'users/create_job.html', {'form': form})




from django.shortcuts import render, get_object_or_404, redirect
from .models import JobPosting
from .forms import JobPostingForm

def job_drafts(request):
    drafts = JobPosting.objects.filter(status='draft')  # Assuming 'status' is a field in your model
    return render(request, 'users/job_drafts.html', {'drafts': drafts})

def edit_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_drafts')
    else:
        form = JobPostingForm(instance=job)
    return render(request, 'users/job_creation.html', {'form': form})

def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('job_drafts')
    return render(request, 'users/job_delete_confirm.html', {'job': job})

from django.shortcuts import render, get_object_or_404, redirect
from .models import JobPosting

def published_jobs(request):
    jobs = JobPosting.objects.filter(is_published=True)
    return render(request, 'users/published_jobs.html', {'jobs': jobs})

def view_job(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    return render(request, 'users/view_job.html', {'job': job})

def edit_job(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    if request.method == 'POST':
        # Handle form submission for editing job
        pass
    return render(request, 'users/create_job.html', {'job': job})

def unpublish_job(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    if request.method == 'POST':
        job.is_published = False
        job.save()
        return redirect('published_jobs')
    return render(request, 'users/confirm_unpublish.html', {'job': job})

from django.shortcuts import render, redirect, get_object_or_404
from .models import JobCategory
from .forms import JobCategoryForm

def job_categories(request):
    categories = JobCategory.objects.all()
    return render(request, 'users/job_categories.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        form = JobCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_categories')
    else:
        form = JobCategoryForm()
    return render(request, 'users/add_category.html', {'form': form})

def edit_category(request, category_id):
    category = get_object_or_404(JobCategory, pk=category_id)
    if request.method == 'POST':
        form = JobCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('job_categories')
    else:
        form = JobCategoryForm(instance=category)
    return render(request, 'users/edit_category.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(JobCategory, pk=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('job_categories')
    return render(request, 'users/confirm_delete.html', {'category': category})

from django.shortcuts import render, get_object_or_404, redirect
from .models import JobCategory
from .forms import JobCategoryForm

def edit_category(request, category_id):
    category = get_object_or_404(JobCategory, pk=category_id)
    if request.method == 'POST':
        form = JobCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('job_categories')
    else:
        form = JobCategoryForm(instance=category)
    return render(request, 'users/edit_category_modal.html', {'form': form, 'category': category})


# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ApplicationForm
from .forms import ApplicationFormForm

def application_forms_management(request):
    forms = ApplicationForm.objects.all()
    return render(request, 'users/application_forms_management.html', {'forms': forms})

def create_application_form(request):
    if request.method == 'POST':
        form = ApplicationFormForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application form created successfully.')
            return redirect('application_forms_management')
    else:
        form = ApplicationFormForm()
    return render(request, 'users/create_application_form.html', {'form': form})

def edit_application_form(request, form_id):
    application_form = get_object_or_404(ApplicationForm, id=form_id)
    if request.method == 'POST':
        form = ApplicationFormForm(request.POST, instance=application_form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application form updated successfully.')
            return redirect('application_forms_management')
    else:
        form = ApplicationFormForm(instance=application_form)
    return render(request, 'users/edit_application_form.html', {'form': form})

def delete_application_form(request, form_id):
    application_form = get_object_or_404(ApplicationForm, id=form_id)
    if request.method == 'POST':
        application_form.delete()
        messages.success(request, 'Application form deleted successfully.')
        return redirect('application_forms_management')
    return render(request, 'users/delete_application_form_confirm.html', {'form': application_form})

# users/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ApplicationForm, JobPosting
from .forms import ApplicationFormForm

def create_application_form(request):
    if request.method == 'POST':
        form = ApplicationFormForm(request.POST)
        if form.is_valid():
            application_form = form.save()
            # Handle form fields (parse JSON, if needed)
            messages.success(request, 'Application form created successfully.')
            return redirect('application_forms_management')
    else:
        form = ApplicationFormForm()
    
    jobs = JobPosting.objects.all()
    return render(request, 'users/create_application_form.html', {'form': form, 'jobs': jobs})

from django.shortcuts import render, get_object_or_404, redirect
from .models import ApplicationForm, JobPosting
from .forms import ApplicationForm as ApplicationFormForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import ApplicationForm, JobPosting
from .forms import ApplicationFormForm

def edit_form(request, form_id):
    # Retrieve the form instance based on the provided form_id
    form_instance = get_object_or_404(ApplicationForm, id=form_id)
    
    # Handle form submission
    if request.method == 'POST':
        form = ApplicationFormForm(request.POST, instance=form_instance)
        if form.is_valid():
            form.save()
            # Redirect to a page showing all forms
            return redirect('application_forms_management')  
    else:
        # Initialize the form with the existing form_instance
        form = ApplicationFormForm(instance=form_instance)
    
    # Fetch all job postings for the associated job dropdown
    jobs = JobPosting.objects.all()
    
    # Pass the form, jobs, and form_instance to the template
    context = {
        'form': form,
        'jobs': jobs,
        'form_instance': form_instance
    }
    
    # Render the edit form template with the context data
    return render(request, 'users/edit_application_form.html', context)

# users/views.py

from django.shortcuts import render
from .models import Application
from django.db.models import Count
from django.utils import timezone
import datetime

# users/views.py

from django.core.serializers.json import DjangoJSONEncoder
import json

def dashboard(request):
    # Handle date range filter
    start_date = request.GET.get('start_date', timezone.now() - datetime.timedelta(days=30))
    end_date = request.GET.get('end_date', timezone.now())
    
    applications = Application.objects.filter(date_applied__range=[start_date, end_date])
    
    # Calculate metrics
    total_applications = applications.count()
    applications_in_progress = applications.filter(status='In Progress').count()
    hired_candidates = applications.filter(status='Hired').count()
    rejected_candidates = applications.filter(status='Rejected').count()
    
    # Aggregate data for charts
    applications_over_time = applications.values('date_applied').annotate(total=Count('id')).order_by('date_applied')
    applications_by_source = applications.values('source').annotate(total=Count('id'))
    applications_by_status = applications.values('status').annotate(total=Count('id'))
    
    # Prepare data for charts
    context = {
        'total_applications': total_applications,
        'applications_in_progress': applications_in_progress,
        'hired_candidates': hired_candidates,
        'rejected_candidates': rejected_candidates,
        'applications_over_time_labels': json.dumps([item['date_applied'] for item in applications_over_time]),
        'applications_over_time_values': json.dumps([item['total'] for item in applications_over_time]),
        'applications_by_source_labels': json.dumps([item['source'] for item in applications_by_source]),
        'applications_by_source_values': json.dumps([item['total'] for item in applications_by_source]),
        'applications_by_status_labels': json.dumps([item['status'] for item in applications_by_status]),
        'applications_by_status_values': json.dumps([item['total'] for item in applications_by_status]),
    }
    return render(request, 'users/dashboard.html', context)





from django.shortcuts import get_object_or_404, redirect
from .models import Application

from django.shortcuts import render, get_object_or_404
from .models import Application  # Make sure Application model is correctly defined

def view_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    context = {
        'application': application
    }
    return render(request, 'users/view_application.html', context)



def move_to_next_stage(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    # Logic to move the application to the next stage
    application.status = 'Next Stage'  # Example status update
    application.save()
    return redirect('dashboard')

def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    # Logic to reject the application
    application.status = 'Rejected'
    application.save()
    return redirect('dashboard')

from django.shortcuts import render, redirect
from .models import Application, JobPosting

def applications_management(request):
    job_title = request.GET.get('job_title')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    applications = Application.objects.all()

    if job_title:
        applications = applications.filter(job_title__title=job_title)
    if status:
        applications = applications.filter(status=status)
    if date_from and date_to:
        applications = applications.filter(date_applied__range=[date_from, date_to])

    jobs = JobPosting.objects.all()

    context = {
        'applications': applications,
        'jobs': jobs
    }
    return render(request, 'users/applications_management.html', context)

from django.shortcuts import redirect, get_object_or_404
from .models import Application  # Ensure this import is correct

def move_to_next_stage(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Example logic for moving to the next stage
    # Assuming stages are: Applied -> In Review -> Interview -> Offered -> Rejected
    stages = ['Applied', 'In Review', 'Interview', 'Offered', 'Rejected']
    
    if application.status in stages:
        current_index = stages.index(application.status)
        if current_index < len(stages) - 1:
            application.status = stages[current_index + 1]
            application.save()
    
    return redirect('applications_management')  # Redirect to applications management or relevant page


from django.shortcuts import redirect, get_object_or_404
from .models import Application  # Ensure this import is correct

def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Update the application status to "Rejected"
    application.status = 'Rejected'
    application.save()
    
    return redirect('applications_management')
      # Redirect to applications management or relevant page
from django.shortcuts import render, get_object_or_404
from .models import Application, StatusHistory

def application_details(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    status_history = StatusHistory.objects.filter(application=application).order_by('-date')
    
    context = {
        'application': application,
        'status_history': status_history,
    }
    
    return render(request, 'users/application_details.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification

def notifications_screen(request):
    notifications = Notification.objects.all()

    if request.method == 'POST':
        if 'mark_as_read' in request.POST:
            notification_id = request.POST.get('notification_id')
            notification = get_object_or_404(Notification, id=notification_id)
            notification.read = True
            notification.save()
            return redirect('notifications_screen')  # Redirect to avoid form resubmission
        
        if 'delete' in request.POST:
            notification_id = request.POST.get('notification_id')
            notification = get_object_or_404(Notification, id=notification_id)
            notification.delete()
            return redirect('notifications_screen')  # Redirect to avoid form resubmission

    context = {
        'notifications': notifications,
    }
    return render(request, 'users/notifications_screen.html', context)

# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Interview

def interview_scheduling_dashboard(request):
    interviews = Interview.objects.all()  # Adjust the filter as needed

    if request.method == 'POST':
        if 'cancel' in request.POST:
            interview_id = request.POST.get('interview_id')
            interview = get_object_or_404(Interview, id=interview_id)
            interview.delete()
            return redirect('interview_scheduling_dashboard')

    context = {
        'interviews': interviews,
    }
    return render(request, 'users/interview_scheduling_dashboard.html', context)

# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Interview

def view_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    
    if request.method == 'POST':
        if 'save_status' in request.POST:
            new_status = request.POST.get('status')
            interview.status = new_status
            interview.save()
        elif 'save_notes' in request.POST:
            notes = request.POST.get('notes')
            interview.notes = notes
            interview.save()
        return redirect('view_interview', interview_id=interview.id)

    context = {
        'interview': interview,
    }
    return render(request, 'users/view_interview.html', context)

# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Interview
from .forms import RescheduleInterviewForm
from django.contrib import messages

def reschedule_interview(request, interview_id):
    interview = get_object_or_404(Interview, pk=interview_id)
    
    if request.method == 'POST':
        form = RescheduleInterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview rescheduled successfully.')
            return redirect('interview_details', interview_id=interview.id)
    else:
        form = RescheduleInterviewForm(instance=interview)
    
    context = {
        'form': form,
        'interview': interview,
    }
    return render(request, 'users/reschedule_interview.html', context)



# views.py
from django.shortcuts import render, redirect
from .forms import ScheduleInterviewForm
from .models import Interview



def schedule_interview(request):
    if request.method == 'POST':
        form = ScheduleInterviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interview_scheduling_dashboard')  # Adjust based on your URL pattern
    else:
        form = ScheduleInterviewForm()
    
    return render(request, 'schedule_interview.html', {'form': form})


# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Interview
from .forms import RescheduleInterviewForm
from django.contrib import messages

def interview_details(request, interview_id):
    interview = get_object_or_404(Interview, pk=interview_id)
    
    if request.method == 'POST':
        if 'reschedule' in request.POST:
            return redirect('reschedule_interview', interview_id=interview.id)
        elif 'cancel' in request.POST:
            interview.delete()
            messages.success(request, 'Interview cancelled successfully.')
            return redirect('interview_scheduling_dashboard')
    
    context = {
        'interview': interview,
    }
    return render(request, 'users/interview_details.html', context)


# users/views.py

# users/views.py

# users/views.py

from django.shortcuts import render, redirect
from .forms import UpdateStatusForm

def update_status(request, application_id):
    if request.method == 'POST':
        form = UpdateStatusForm(request.POST)
        if form.is_valid():
            # Extract form data
            new_status = form.cleaned_data['new_status']
            notes = form.cleaned_data['notes']
            
            
            application = Application.objects.get(id=application_id)
            application.status = new_status
            application.save()
            StatusHistory.objects.create(application=application, status=new_status, notes=notes)
            
            return redirect('application_details', application_id=application_id)  # Redirect to application details
    else:
        
        application = Application.objects.get(id=application_id)
        initial_data = {
        'current_status': application.status
        }
        form = UpdateStatusForm(initial={'current_status': 'example_status'})  # Replace with actual status
        
    return render(request, 'users/update_status.html', {'form': form})



# users/views.py

# users/views.py

from django.shortcuts import render, redirect
from .forms import ComposeMessageForm

def compose_message(request):
    if request.method == 'POST':
        form = ComposeMessageForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., send an email)
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Here, you would typically send the email using Django's email framework
            # from django.core.mail import send_mail
            # send_mail(subject, message, 'from@example.com', [recipient])
            
            return redirect('dashboard')  # Or redirect to a success page
    else:
        form = ComposeMessageForm()
    
    return render(request, 'users/compose_message.html', {'form': form})

# users/views.py

from django.shortcuts import render, redirect
from .models import Report  # Assuming you have a Report model

def custom_reports_dashboard(request):
    reports = Report.objects.all()  # Fetch saved reports
    return render(request, 'users/custom_reports_dashboard.html', {'reports': reports})


# users/views.py

from django import forms
from django.shortcuts import render, redirect
from .models import Report

class CreateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['name', 'criteria']  # Adjust fields based on your model

# users/views.py

from django.shortcuts import render, redirect
from .forms import CreateReportForm

def create_report(request):
    if request.method == 'POST':
        form = CreateReportForm(request.POST)
        if form.is_valid():
            # Handle form data and generate the report
            report_name = form.cleaned_data['report_name']
            date_range = form.cleaned_data['date_range']
            status = form.cleaned_data.get('status')
            position = form.cleaned_data.get('position')
            source = form.cleaned_data.get('source')
            fields_to_include = form.cleaned_data['fields_to_include']
            
            # Generate the report based on the criteria
            # (Your logic for generating the report goes here)

            return redirect('custom_reports_dashboard')  # Redirect to the dashboard or report details page
    else:
        form = CreateReportForm()

    return render(request, 'users/create_report.html', {'form': form})


# users/views.py

def view_report(request, report_id):
    report = Report.objects.get(id=report_id)
    return render(request, 'users/view_report.html', {'report': report})

# users/views.py

# users/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreateReportForm
from .models import Report

def edit_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        form = CreateReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('report_details', report_id=report.id)
    else:
        form = CreateReportForm(instance=report)

    return render(request, 'users/edit_report.html', {'form': form, 'report': report})


# users/views.py

# users/views.py

from django.shortcuts import redirect
from .models import Report

def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.delete()
    return redirect('custom_reports_dashboard')


# users/views.py
# users/views.py

from django.http import HttpResponse
from io import BytesIO
from openpyxl import Workbook
from django.shortcuts import get_object_or_404
from .models import Report

def export_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Fetch the report data and generate a Workbook
    report_data = report.get_report_data()
    wb = Workbook()
    ws = wb.active
    ws.title = "Report Data"
    
    # Add header row
    headers = report_data[0].keys() if report_data else []
    ws.append(headers)
    
    # Add data rows
    for data in report_data:
        ws.append(list(data.values()))
    
    # Create an HTTP response with Excel format
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{report.name}.xlsx"'
    
    # Write the Workbook to a BytesIO stream
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    
    response.write(stream.getvalue())
    return response



# users/views.py

from django.shortcuts import render, get_object_or_404
from .models import Report

def report_details(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Assuming you have a method to get the report data based on selected fields
    report_data = report.get_report_data()  # Define this method in your Report model

    return render(request, 'users/report_details.html', {
        'report': report,
        'report_data': report_data
    })

# users/views.py
# users/views.py

# users/views.py

# users/views.py

from django.shortcuts import render, redirect
from .forms import CreateReportForm
from .models import Report

def create_report_view(request):
    if request.method == 'POST':
        form = CreateReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            # Handle additional fields
            report.filters = {
                'date_range': form.cleaned_data['date_range'],
                'status': form.cleaned_data['status'],
                'position': form.cleaned_data['position'],
                'source': form.cleaned_data['source']
            }
            report.fields = form.cleaned_data['fields_to_include']
            report.created_by = request.user
            report.save()
            return redirect('some_success_url')
    else:
        form = CreateReportForm()

    return render(request, 'users/create_report.html', {'form': form})



