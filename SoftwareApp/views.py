from django.shortcuts import render
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from AdminApp.models import CRMFollowup
import csv
from django.http import HttpResponse
from datetime import date, datetime
from django.contrib import messages
# Create your views here.

def software_welcome_page(request):
    return render(request,'software_welcome.html')

# views.py
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from AdminApp.models import CRMFollowup, Enquiry, Branch

def crm_software_dashboard(request):
    # Get current date and time
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    
    # CRM Follow-up Statistics
    total_followups = CRMFollowup.objects.count()
    new_followups_today = CRMFollowup.objects.filter(created_at__date=today).count()
    followups_this_week = CRMFollowup.objects.filter(created_at__gte=week_ago).count()
    
    # Status-based counts
    interested_leads = CRMFollowup.objects.filter(status='interested').count()
    class_joined = CRMFollowup.objects.filter(status='class_joined').count()
    pending_followups = CRMFollowup.objects.filter(
        Q(next_followup_reminder__lt=now) | Q(next_followup_reminder__isnull=True),
        status__in=['interested', 'planning', 'under_review']
    ).count()
    
    # Priority counts
    high_priority = CRMFollowup.objects.filter(priority='high').count()
    overdue_followups = CRMFollowup.objects.filter(
        next_followup_reminder__lt=now,
        status__in=['interested', 'planning', 'under_review']
    ).count()
    
    # Enquiry Statistics
    total_enquiries = Enquiry.objects.count()
    new_enquiries_today = Enquiry.objects.filter(submitted_at__date=today).count()
    pending_enquiries = Enquiry.objects.filter(remark__isnull=True).count()
    
    # Conversion rate (Leads that joined class vs total leads)
    conversion_rate = round((class_joined / total_followups * 100) if total_followups > 0 else 0, 1)
    
    # Status Distribution
    status_distribution = {}
    for status_choice in CRMFollowup.STATUS:
        count = CRMFollowup.objects.filter(status=status_choice[0]).count()
        status_distribution[status_choice[1]] = count
    
    # Source Distribution
    source_distribution = {}
    for source_choice in CRMFollowup.SOURCE_CHOICES:
        count = CRMFollowup.objects.filter(source=source_choice[0]).count()
        source_distribution[source_choice[1]] = count
    
    # High Priority Follow-ups
    high_priority_followups = CRMFollowup.objects.filter(
        priority='high'
    ).order_by('-next_followup_reminder')[:5]
    
    # Recent Enquiries
    recent_enquiries = Enquiry.objects.order_by('-submitted_at')[:5]
    
    # Recent Activities (simplified)
    recent_activities = []
    
    # Add recent follow-up activities
    recent_followups = CRMFollowup.objects.order_by('-follow_up_date')[:3]
    for followup in recent_followups:
        if followup.follow_up_date:
            recent_activities.append({
                'title': f'Follow-up with {followup.name}',
                'time': followup.follow_up_date.strftime('%I:%M %p'),
                'description': f'Status: {followup.get_status_display()}'
            })
    
    # Add recent enquiries
    for enquiry in recent_enquiries[:2]:
        recent_activities.append({
            'title': f'New enquiry from {enquiry.full_name}',
            'time': enquiry.submitted_at.strftime('%I:%M %p'),
            'description': enquiry.message[:50] + '...' if enquiry.message else ''
        })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    
    # Prepare data for charts
    status_labels = [status[1] for status in CRMFollowup.STATUS]
    status_counts = [CRMFollowup.objects.filter(status=status[0]).count() for status in CRMFollowup.STATUS]
    
    source_labels = [source[1] for source in CRMFollowup.SOURCE_CHOICES]
    source_counts = [CRMFollowup.objects.filter(source=source[0]).count() for source in CRMFollowup.SOURCE_CHOICES]
    
    context = {
        # Stats
        'total_followups': total_followups,
        'new_followups_today': new_followups_today,
        'followups_this_week': followups_this_week,
        'interested_leads': interested_leads,
        'class_joined': class_joined,
        'pending_followups': pending_followups,
        'high_priority': high_priority,
        'overdue_followups': overdue_followups,
        
        # Enquiries
        'total_enquiries': total_enquiries,
        'new_enquiries_today': new_enquiries_today,
        'pending_enquiries': pending_enquiries,
        'conversion_rate': conversion_rate,
        
        # Distributions
        'status_distribution': status_distribution,
        'source_distribution': source_distribution,
        
        # Recent Data
        'high_priority_followups': high_priority_followups,
        'recent_enquiries': recent_enquiries,
        'recent_activities': recent_activities,
        
        # Chart Data
        'status_labels': status_labels,
        'status_counts': status_counts,
        'source_labels': source_labels,
        'source_counts': source_counts,
    } 
    return render(request, 'crm_software_dashboard.html', context)

@login_required
def crm_follow_up_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    branch = request.GET.get('branch', '')
    address = request.GET.get('address', '')
    
    # Start with all follow-ups
    followups = CRMFollowup.objects.all().order_by('-follow_up_date')
    brances=Branch.objects.all()
    # Apply filters
    if search_query:
        followups = followups.filter(
            Q(name__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(follow_up_notes__icontains=search_query) |
            Q(address__icontains=search_query) 
        )
    
    if status_filter:
        followups = followups.filter(status=status_filter)
    
    if priority_filter:
        followups = followups.filter(priority=priority_filter)
    
    if branch:
        followups = followups.filter(branch=branch)
    
    if address:
        print( "Address Filter Applied:", address)
        followups = followups.filter(address__icontains=address)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            followups = followups.filter(follow_up_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            followups = followups.filter(follow_up_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate stats
    total_leads = followups.count()
    high_priority = followups.filter(priority='high').count()
    
    # Get today's follow-ups
    today = date.today()
    today_followups = followups.filter(
        follow_up_date__date=today
    ).count()
    
    # Get pending follow-ups (where next_followup_reminder is in past)
    from django.utils import timezone
    pending_followups = followups.filter(
        next_followup_reminder__lt=timezone.now(),
        status__in=['interested', 'planning', 'under_review']
    ).count()
    
    # Add overdue flag to each followup
    for followup in followups:
        followup.is_overdue = (
            followup.next_followup_reminder and 
            followup.next_followup_reminder < timezone.now()
        )
    
    # Pagination
    paginator = Paginator(followups, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'followups': page_obj,
        'total_leads': total_leads,
        'high_priority': high_priority,
        'today_followups': today_followups,
        'pending_followups': pending_followups,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': brances,
    }
    
    return render(request, 'crm_follow_up_list.html', context)

@login_required
def export_followups(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="followups_export.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow([
        'Name', 'Mobile Number', 'Status', 'Priority', 'Source',
        'Follow-up Date', 'Next Follow-up', 
        'Class Start Date', 'Created At','address','branch','Follow-up Notes'
    ])
    
    # Get all follow-ups
    followups = CRMFollowup.objects.all()
    
    # Write data rows
    for followup in followups:
        writer.writerow([
            followup.name,
            followup.mobile_number,
            followup.get_status_display(),
            followup.get_priority_display(),
            followup.get_source_display(),
            followup.follow_up_date.strftime('%Y-%m-%d %H:%M') if followup.follow_up_date else '',
            followup.next_followup_reminder.strftime('%Y-%m-%d %H:%M') if followup.next_followup_reminder else '',
            followup.class_start_date.strftime('%Y-%m-%d %H:%M') if followup.class_start_date else '',
            followup.created_at.strftime('%Y-%m-%d %H:%M'),
            followup.address or '',
            followup.branch or '',
            followup.follow_up_notes or '',
        ])
    
    return response

@login_required
def download_template(request):
    # Create template CSV file for import
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="followup_template.csv"'
    
    writer = csv.writer(response)
    # Write header row with example data
    writer.writerow([
        'Name', 'Mobile Number', 'Status', 'Priority', 'Source',
        'Follow-up Notes', 'Address', 'Branch'
    ])
    writer.writerow([
        'John Doe', '9876543210', 'interested', 'high', 'website', 
        'Interested in Python course', 'Pune', 'Main Branch'
    ])
    writer.writerow([
        'Jane Smith', '9876543211', 'planning', 'medium', 'whatsapp', 
        'Planning to join next month', 'Mumbai', 'Secondary Branch'
    ])
    
    return response


@login_required
def import_followups(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if file is CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
            return redirect('crm_follow_up_list')
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            imported_count = 0
            duplicates = []  # List to store duplicate records
            
            # First pass: Check for duplicates
            rows_to_process = []
            for row in reader:
                mobile_number = row.get('Mobile Number', '').strip()
                name = row.get('Name', '').strip()
                
                # Check if mobile number already exists in database
                if CRMFollowup.objects.filter(mobile_number=mobile_number).exists():
                    duplicates.append(f"{name} - {mobile_number}")
                else:
                    rows_to_process.append(row)
            
            # If duplicates found, stop and show error
            if duplicates:
                duplicate_list = "<br>".join(duplicates)
                messages.error(
                    request, 
                    f'<b>Bulk import stopped! Found {len(duplicates)} duplicate mobile numbers:<b> <br><br> {duplicate_list}'
                )
                print(duplicate_list)
                return redirect('crm_follow_up_list')
            
            # Second pass: Import only non-duplicate records
            for row in rows_to_process:
                # Handle branch - get or create based on CSV value
                branch_name = row.get('Branch', '').strip()
                branch_instance = None
                
                if branch_name:
                    # Try to find existing branch
                    branch_qs = Branch.objects.filter(branch_name__iexact=branch_name)
                    if branch_qs.exists():
                        branch_instance = branch_qs.first()
                    else:
                        # Create new branch if it doesn't exist
                        branch_instance = Branch.objects.create(branch_name=branch_name)
                
                # Create new follow-up from CSV data
                CRMFollowup.objects.create(
                    name=row.get('Name', '').strip(),
                    mobile_number=row.get('Mobile Number', '').strip(),
                    status=row.get('Status', 'interested').lower().strip(),
                    priority=row.get('Priority', 'medium').lower().strip(),
                    source=row.get('Source', 'website').lower().strip(),
                    follow_up_notes=row.get('Follow-up Notes', '').strip(),
                    address=row.get('Address', '').strip(),
                    branch=branch_instance,
                    follow_up_by=request.user,
                )
                imported_count += 1
            
            messages.success(request, f'Successfully Bulk imported {imported_count} follow-ups')
        
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
    return redirect('crm_follow_up_list')



 # views.py
# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .forms import CRMFollowupUpdateForm

@login_required
def followup_detail(request, pk):
    """View follow-up details"""
    followup = get_object_or_404(CRMFollowup, pk=pk)
    form = CRMFollowupUpdateForm(instance=followup)
    
    # Get history
    history_list = []
    try:
        history_records = followup.history.all().order_by('-history_date')
        for i, record in enumerate(history_records):
            history_item = {
                'record': record,
                'history_date': record.history_date,
                'history_user': record.history_user,
                'history_change_reason': record.history_change_reason,
                'prev_record': history_records[i + 1] if i < len(history_records) - 1 else None,
                'get_changes': {}
            }
            
            if history_item['prev_record']:
                changes = get_detailed_changes(history_item['prev_record'], record)
                history_item['get_changes'] = changes
            
            history_list.append(history_item)
    except Exception as e:
        print(f"Error loading history: {e}")
    
    context = {
        'followup': followup,
        'form': form,
        'history': history_list,
    }
    
    return render(request, 'crm_follow_up_details.html', context)


def update_followup(request, id): 
    followup = get_object_or_404(CRMFollowup, id=id)
    
    if request.method == 'POST':
        form = CRMFollowupUpdateForm(request.POST, request.FILES, instance=followup)
        
        if form.is_valid():
            fm=form.save(commit=False)
            fm.follow_up_by = request.user
            fm.save()
            messages.success(request, 'Follow-up updated successfully.')
            # Return JavaScript to close window
            return HttpResponse("""
                <script>
                    if (window.opener && !window.opener.closed) {
                        window.opener.location.reload();  // Refresh parent page
                    }
                    window.close();  // Close this window
                </script>
            """)
        else:
            # If form has errors, show them on the same page
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CRMFollowupUpdateForm(instance=followup)
    
    return render(request, 'crm_update_follow_up.html', {'form': form})



def create_followup(request): 
    
    if request.method == 'POST':
        form = CRMFollowupUpdateForm(request.POST, request.FILES)
        
        if form.is_valid():
            fm=form.save(commit=False)
            fm.follow_up_by = request.user
            fm.save()
            messages.success(request, 'Follow-up Created successfully.')
            # Return JavaScript to close window
            return HttpResponse("""
                <script>
                    if (window.opener && !window.opener.closed) {
                        window.opener.location.reload();  // Refresh parent page
                    }
                    window.close();  // Close this window
                </script>
            """)
        else:
            # If form has errors, show them on the same page
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CRMFollowupUpdateForm()
    
    return render(request, 'crm_create_follow_up.html', {'form': form})


def get_detailed_changes(old_record, new_record):
    """Get detailed field changes between records with better formatting"""
    changes = {}
    
    # Define field labels for better display
    field_labels = {
        'name': 'Name',
        'mobile_number': 'Mobile Number',
        'status': 'Status',
        'priority': 'Priority',
        'source': 'Source',
        'call_response': 'Call Response',
        'follow_up_date': 'Follow-up Date',
        'next_followup_reminder': 'Next Follow-up',
        'class_start_date': 'Class Start Date',
        'follow_up_notes': 'Notes',
        'student_interested_for': 'Interested Course',
        'follow_up_by': 'Assigned To',
    }
    
    # Get all model fields
    fields = [f.name for f in CRMFollowup._meta.get_fields() 
              if f.name not in ['id', 'history', 'created_at', 'updated_at']]
    
    for field in fields:
        old_value = getattr(old_record, field, None)
        new_value = getattr(new_record, field, None)
        
        # Skip if values are the same
        if old_value == new_value:
            continue
            
        # Handle different field types
        if field in ['status', 'priority', 'source', 'call_response']:
            # Get choice display values
            choices_dict = {
                'status': dict(CRMFollowup.STATUS),
                'priority': dict(CRMFollowup.PRIORITY_CHOICES),
                'source': dict(CRMFollowup.SOURCE_CHOICES),
                'call_response': dict(CRMFollowup.CALL_RESPONSE_CHOICES),
            }
            
            old_display = choices_dict.get(field, {}).get(old_value, str(old_value))
            new_display = choices_dict.get(field, {}).get(new_value, str(new_value))
            
            changes[field_labels.get(field, field)] = (old_display, new_display)
            
        elif field.endswith('_id'):
            # Handle foreign key fields
            related_field = field.replace('_id', '')
            try:
                old_obj = getattr(old_record, related_field, None)
                new_obj = getattr(new_record, related_field, None)
                changes[field_labels.get(related_field, related_field)] = (
                    str(old_obj) if old_obj else 'None',
                    str(new_obj) if new_obj else 'None'
                )
            except:
                changes[field_labels.get(related_field, related_field)] = (
                    str(old_value) if old_value else 'None',
                    str(new_value) if new_value else 'None'
                )
                
        elif 'date' in field or 'reminder' in field:
            # Format datetime fields
            old_display = old_value.strftime("%b %d, %Y %H:%M") if old_value else "Not set"
            new_display = new_value.strftime("%b %d, %Y %H:%M") if new_value else "Not set"
            changes[field_labels.get(field, field)] = (old_display, new_display)
            
        elif field == 'follow_up_notes':
            # Handle notes - show truncated version
            old_display = truncate_text(str(old_value or ''), 50)
            new_display = truncate_text(str(new_value or ''), 50)
            changes[field_labels.get(field, field)] = (old_display, new_display)
            
        else:
            # Default handling
            changes[field_labels.get(field, field)] = (
                str(old_value) if old_value is not None else 'Not set',
                str(new_value) if new_value is not None else 'Not set'
            )
    
    return changes

def truncate_text(text, max_length):
    """Truncate text for display"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

from django.views.decorators.http import require_POST
from django.http import HttpResponse


@login_required
def enquiry_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all enquiries
    enquiries = Enquiry.objects.all().order_by('-submitted_at')
    
    # Apply filters
    if search_query:
        enquiries = enquiries.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    if status_filter == 'pending':
        enquiries = enquiries.filter(is_added_in_CRMFollowup_model=False)
    elif status_filter == 'added':
        enquiries = enquiries.filter(is_added_in_CRMFollowup_model=True)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            enquiries = enquiries.filter(submitted_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            enquiries = enquiries.filter(submitted_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(enquiries, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'enquiries': page_obj,
    }
    
    return render(request, 'crm_enquiry_list.html', context)

@login_required
def add_to_followup(request, enquiry_id):
    """Add enquiry to CRMFollowup model"""
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    
    mobile_number = enquiry.phone.strip()
    follow_up_exists = CRMFollowup.objects.filter(mobile_number=mobile_number).exists()
    if follow_up_exists:
        messages.error(request, f'A follow-up with {mobile_number} mobile number already exists in CRM.')
        return redirect(request.META.get('HTTP_REFERER', 'crm_enquiry_list'))   
    # Check if already added
    if enquiry.is_added_in_CRMFollowup_model:
        messages.info(request, 'This enquiry is already added to follow-up list.')
        #return to currect page
        return redirect(request.META.get('HTTP_REFERER', 'crm_enquiry_list'))   
    
    try:

        # Create new CRMFollowup from enquiry
        followup = CRMFollowup.objects.create(
            name=enquiry.full_name,
            mobile_number=enquiry.phone,
            source='website',  # Default source
            follow_up_notes=f"Enquiry from website: {enquiry.message[:500]}",  # Truncate if too long
            # Other fields will remain null/blank
        )
        
        # Update enquiry flag
        enquiry.is_added_in_CRMFollowup_model = True
        enquiry.save()
        messages.success(request, f'Enquiry from {enquiry.full_name} has been added to follow-up list.')
        return redirect(request.META.get('HTTP_REFERER', 'crm_enquiry_list'))   
       
    except Exception as e: 
        messages.error(request, f'Error adding to follow-up list: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'crm_enquiry_list'))   
 


@login_required
def export_enquiries(request):
    """Export enquiries to CSV"""
    # Similar filtering logic as enquiry_list
    enquiries = Enquiry.objects.all().order_by('-submitted_at')
    
    # Apply filters from request
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        enquiries = enquiries.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if status_filter == 'pending':
        enquiries = enquiries.filter(is_added_in_CRMFollowup_model=False)
    elif status_filter == 'added':
        enquiries = enquiries.filter(is_added_in_CRMFollowup_model=True)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enquiries_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Phone', 'Email', 'Message', 'Submitted At', 'Remark', 'Added to Follow-up'])
    
    for enquiry in enquiries:
        writer.writerow([
            enquiry.full_name,
            enquiry.phone,
            enquiry.email,
            enquiry.message,
            enquiry.submitted_at.strftime('%Y-%m-%d %H:%M'),
            enquiry.remark or '',
            'Yes' if enquiry.is_added_in_CRMFollowup_model else 'No'
        ])
    
    return response

def delete_follow_up(request, id):
    # Retrieve the follow-up record by ID or 404 if not found
    rec = get_object_or_404(CRMFollowup, id=id)
    
    if rec:
        # Delete the record
        rec.delete()
        
        # Display success message
        messages.success(request, 'Follow-up record deleted successfully.')

    # Redirect back to the page the user came from
    return redirect(request.META.get('HTTP_REFERER', '/software/followups'))