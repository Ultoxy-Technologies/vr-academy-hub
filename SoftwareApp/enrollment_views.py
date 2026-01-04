# views.py (enrollment section)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from decimal import Decimal
from AdminApp.models import *
from .forms import EnrollmentForm, BatchForm

def enrollment_dashboard(request):
     
    return render(request, 'enrollment_dashboard.html')


@login_required
def enrolled_student_list(request):
    """
    List all enrollments with filtering, pagination, and statistics
    Follows the exact pattern of crm_follow_up_list
    """
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    batch_filter = request.GET.get('batch', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    payment_status_filter = request.GET.get('payment_status', '')
    
    # Start with all enrollments
    enrollments = Enrollment.objects.all().select_related(
        'student', 'batch', 'batch__basic_to_advance_cource', 'batch__advance_to_pro_cource'
    ).prefetch_related('payments').order_by('-enrollment_date')
    
    # Get all batches for filter dropdown
    batches = Batch.objects.filter(is_active=True).order_by('batch_code')
    
    # Apply filters
    if search_query:
        enrollments = enrollments.filter(
            Q(student__name__icontains=search_query) |
            Q(student__mobile_number__icontains=search_query) |
            Q(course_title__icontains=search_query)
        )
    
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
    
    if batch_filter:
        enrollments = enrollments.filter(batch_id=batch_filter)
    
    if payment_status_filter:
        enrollments = enrollments.filter(payment_status=payment_status_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            enrollments = enrollments.filter(enrollment_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            enrollments = enrollments.filter(enrollment_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate statistics
    total_enrollments = enrollments.count()
    active_enrollments = enrollments.filter(status='active').count()
    completed_enrollments = enrollments.filter(status='completed').count()
    pending_payments = enrollments.filter(payment_status__in=['pending', 'partial', 'overdue']).count()
    
    # Today's enrollments - FIXED
    today = date.today()
    today_enrollments = enrollments.filter(enrollment_date=today).count()
    
    # Calculate payment data for each enrollment efficiently
    total_revenue = Decimal('0.00')
    pending_revenue = Decimal('0.00')
    today = date.today()
    
    for enrollment in enrollments:
        # Calculate paid amount from prefetched payments
        paid_amount = sum(payment.amount for payment in enrollment.payments.all())
        enrollment.display_paid = paid_amount
        enrollment.display_balance = max(enrollment.net_fees - paid_amount, Decimal('0.00'))
        
        # Calculate progress
        if enrollment.net_fees > 0:
            enrollment.display_progress = min((paid_amount / enrollment.net_fees * 100), 100)
        else:
            enrollment.display_progress = 100
        
        # Days since enrollment
        enrollment.days_since_enrollment = (today - enrollment.enrollment_date).days
        
        # Check if enrollment is overdue
        enrollment.is_payment_overdue = (
            enrollment.display_balance > 0 and 
            enrollment.class_start_date and 
            enrollment.class_start_date <= today
        )
        
        # Generate enrollment ID for display
        enrollment.enrollment_id_display = f"ENR-{str(enrollment.pk).zfill(6)}"
        
        # Add to totals
        total_revenue += paid_amount
        pending_revenue += enrollment.display_balance
    
    # Pagination
    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare context
    context = {
        'enrollments': page_obj,
        'batches': batches,
        
        # Statistics
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'pending_payments': pending_payments,
        'today_enrollments': today_enrollments,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        
        # Filter values
        'search_query': search_query,
        'status_filter': status_filter,
        'batch_filter': batch_filter,
        'payment_status_filter': payment_status_filter,
        'date_from': date_from,
        'date_to': date_to,
        
        # Status choices
        'status_choices': Enrollment.STATUS_CHOICES,
        'payment_status_choices': Enrollment.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'enrolled_student_list.html', context)




# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal 
from django import forms

@login_required
def enrollment_detail(request, pk):
    """View enrollment details with payment history and certificate info"""
    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            'student', 'batch', 'batch__basic_to_advance_cource', 'batch__advance_to_pro_cource'
        ).prefetch_related('payments', 'payments__received_by'),
        pk=pk
    )
    
    # Get all payments for this enrollment
    payments = enrollment.payments.all().order_by('-payment_date')
    
    # Calculate payment statistics
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_due = enrollment.balance
    
    # Get payment summary by type
    payment_by_type = {}
    for payment_type, display_name in Payment.PAYMENT_TYPE_CHOICES:
        amount = payments.filter(payment_type=payment_type).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        if amount > 0:
            payment_by_type[display_name] = amount
    
    # Get certificate if exists
    certificate = None
    try:
        certificate = StudentCertificate.objects.get(enrollment=enrollment)
    except StudentCertificate.DoesNotExist:
        certificate = None
    
    # Calculate days since enrollment
    days_since_enrollment = (timezone.now().date() - enrollment.enrollment_date).days
    
    # Calculate class progress percentage
    class_progress = 0
    if enrollment.class_start_date and enrollment.class_end_date:
        total_days = (enrollment.class_end_date - enrollment.class_start_date).days
        if total_days > 0:
            days_passed = (timezone.now().date() - enrollment.class_start_date).days
            class_progress = min(max((days_passed / total_days) * 100, 0), 100)
    
    # Check if enrollment is overdue
    is_overdue = (
        total_due > 0 and 
        enrollment.class_start_date and 
        enrollment.class_start_date <= timezone.now().date()
    )
    
    # Get batch details
    batch = enrollment.batch
    batch_details = {
        'start_date': batch.start_date,
        'end_date': batch.end_date,
        'is_active': batch.is_active,
        'course_type': batch.course_type,
        'course_fees': batch.course_fees,
    }
    
    # Payment form for quick payment recording
    # payment_form = PaymentForm()
    # payment_form.fields['enrollment'].initial = enrollment
    # payment_form.fields['enrollment'].widget = forms.HiddenInput()
    
    context = {
        'enrollment': enrollment,
        'payments': payments,
        'total_paid': total_paid,
        'total_due': total_due,
        'payment_by_type': payment_by_type,
        'certificate': certificate,
        'days_since_enrollment': days_since_enrollment,
        'class_progress': class_progress,
        'is_overdue': is_overdue,
        'batch_details': batch_details,
        # 'payment_form': payment_form,
        
        # For progress bars
        'payment_progress': enrollment.payment_progress,
        'total_installments': enrollment.total_installments if hasattr(enrollment, 'total_installments') else 0,
        'paid_installments': enrollment.paid_installments if hasattr(enrollment, 'paid_installments') else 0,
    }
    
    return render(request, 'enrollment_details.html', context)




@login_required
def export_enrollments(request):
    """
    Export enrollments to CSV (following export_followups pattern)
    """
    import csv
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enrollments_export_{}.csv"'.format(
        date.today().strftime('%Y%m%d')
    )
    
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Enrollment ID', 'Student Name', 'Mobile Number', 'Batch',
        'Course', 'Enrollment Date', 'Status', 'Payment Status',
        'Total Fees', 'Discount', 'Net Fees', 'Paid Amount', 'Balance',
        'Class Start Date', 'Class End Date', 'Created At'
    ])
    
    # Get all enrollments with related data
    enrollments = Enrollment.objects.all().select_related(
        'student', 'batch'
    )
    
    # Write data rows
    for enrollment in enrollments:
        # Get course title from batch
        course_title = "Unknown"
        if enrollment.batch:
            if enrollment.batch.basic_to_advance_cource:
                course_title = enrollment.batch.basic_to_advance_cource.title
            elif enrollment.batch.advance_to_pro_cource:
                course_title = enrollment.batch.advance_to_pro_cource.title
        
        writer.writerow([
            enrollment.enrollment_id,
            enrollment.student.name if enrollment.student else '',
            enrollment.student.mobile_number if enrollment.student else '',
            enrollment.batch.batch_title if enrollment.batch else '',
            course_title,
            enrollment.enrollment_date.strftime('%Y-%m-%d'),
            enrollment.get_status_display(),
            enrollment.get_payment_status_display(),
            str(enrollment.total_fees),
            str(enrollment.discount),
            str(enrollment.net_fees),
            str(enrollment.paid_amount),
            str(enrollment.balance),
            enrollment.class_start_date.strftime('%Y-%m-%d') if enrollment.class_start_date else '',
            enrollment.class_end_date.strftime('%Y-%m-%d') if enrollment.class_end_date else '',
            enrollment.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(enrollment, 'created_at') else '',
        ])
    
    return response


@login_required
def download_enrollment_template(request):
    """
    Download template CSV file for enrollment import
    """
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enrollment_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header row with example data
    writer.writerow([
        'Student Name', 'Mobile Number', 'Batch Code', 
        'Total Fees', 'Discount', 'Status', 'Payment Status'
    ])
    
    # Example rows
    writer.writerow([
        'John Doe', '9876543210', 'BATCH-2024-001',
        '15000.00', '1000.00', 'active', 'pending'
    ])
    
    writer.writerow([
        'Jane Smith', '9876543211', 'BATCH-2024-002',
        '20000.00', '0.00', 'active', 'partial'
    ])
    
    return response

import csv
from decimal import Decimal
from .forms import PaymentForm

@login_required
def import_enrollments(request):
    """
    Import enrollments from CSV (following import_followups pattern)
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if file is CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
            return redirect('enrolled_student_list')
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # start=2 for header row
                try:
                    # Get student by mobile number or name
                    mobile_number = row.get('Mobile Number', '').strip()
                    student_name = row.get('Student Name', '').strip()
                    
                    # Find or create student
                    student = None
                    if mobile_number:
                        student = CustomUser.objects.filter(mobile_number=mobile_number).first()
                    
                    if not student and student_name:
                        # Try to find by name
                        student = CustomUser.objects.filter(name__icontains=student_name).first()
                    
                    if not student:
                        errors.append(f"Row {row_num}: Student not found ({student_name} - {mobile_number})")
                        continue
                    
                    # Get batch
                    batch_code = row.get('Batch Code', '').strip()
                    batch = None
                    if batch_code:
                        batch = Batch.objects.filter(batch_code=batch_code).first()
                    
                    if not batch:
                        errors.append(f"Row {row_num}: Batch not found ({batch_code})")
                        continue
                    
                    # Parse numeric values
                    try:
                        total_fees = Decimal(row.get('Total Fees', '0').strip())
                        discount = Decimal(row.get('Discount', '0').strip())
                    except:
                        errors.append(f"Row {row_num}: Invalid fee/discount format")
                        continue
                    
                    # Create enrollment
                    Enrollment.objects.create(
                        student=student,
                        batch=batch,
                        total_fees=total_fees,
                        discount=discount,
                        status=row.get('Status', 'active').strip(),
                        payment_status=row.get('Payment Status', 'pending').strip(),
                        enrollment_date=timezone.now().date(),
                    )
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Show results
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} enrollments')
            
            if errors:
                error_list = "<br>".join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    error_list += f"<br>... and {len(errors) - 10} more errors"
                messages.warning(request, f'Import completed with errors:<br>{error_list}')
        
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
    return redirect('enrolled_student_list')


@login_required
def record_payment(request, enrollment_id):
    """Record a new payment for enrollment"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Calculate payment statistics with safe defaults
    payment_stats = {
        'total_fees': enrollment.total_fees or Decimal('0.00'),
        'discount': enrollment.discount or Decimal('0.00'),
        'net_fees': enrollment.net_fees or Decimal('0.00'),
        'paid_amount': enrollment.paid_amount,
        'balance': enrollment.balance,
        'payment_progress': enrollment.payment_progress or 0,
    }
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, enrollment=enrollment, request=request)
        
        if form.is_valid():
            try:
                payment = form.save()
                
                # Update payment status message based on balance
                new_balance = enrollment.balance
                if new_balance <= 0:
                    status_msg = "Fully Paid! All fees have been cleared."
                else:
                    status_msg = f"Payment recorded. Remaining balance: ₹{new_balance}"
                
                messages.success(
                    request, 
                    f'Payment of ₹{payment.amount} recorded successfully for {enrollment.student.name}. {status_msg}'
                )
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error recording payment: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = PaymentForm(enrollment=enrollment, request=request)
    
    # Get payment history
    payment_history = enrollment.payments.all().order_by('-payment_date')
    
    context = {
        'form': form,
        'enrollment': enrollment,
        'payment_stats': payment_stats,
        'payment_history': payment_history,
    }
    
    return render(request, 'record_payment.html', context)

@login_required
def update_payment(request, pk):
    """Update existing payment"""
    payment = get_object_or_404(Payment, pk=pk)
    enrollment = payment.enrollment
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment, enrollment=enrollment, request=request)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Payment updated successfully')
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error updating payment: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = PaymentForm(instance=payment, enrollment=enrollment, request=request)
    
    context = {
        'form': form,
        'payment': payment,
        'enrollment': enrollment,
    }
    
    return render(request, 'update_payment.html', context)

@login_required
def delete_payment(request, pk):
    """Delete payment with confirmation"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        amount = payment.amount
        student_name = payment.enrollment.student.name
        payment.delete()
        
        # Update enrollment payment status
        payment.enrollment.update_payment_status()
        payment.enrollment.save()
        
        messages.success(request, f'Payment of ₹{amount} deleted for {student_name}')
        return redirect('payment_list')
    
    # For GET request, should be handled by JavaScript modal
    return redirect('payment_list')


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .forms import EnrollmentForm

@login_required
def create_enrollment(request):
    """Create new enrollment (opens in modal window)"""
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, request=request)
        
        if form.is_valid():
            try:
                enrollment = form.save(commit=True)
                messages.success(request, f'Enrollment created successfully for {enrollment.student.name}')
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error creating enrollment: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = EnrollmentForm(request=request)
    
    return render(request, 'enrollment_create.html', {'form': form})

@login_required
def update_enrollment(request, pk):
    """Update existing enrollment (opens in modal window)"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment, request=request, is_update=True)
        
        if form.is_valid():
            try:
                enrollment = form.save(commit=True)
                messages.success(request, f'Enrollment updated successfully for {enrollment.student.name}')
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error updating enrollment: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = EnrollmentForm(instance=enrollment, request=request, is_update=True)
    
    return render(request, 'enrollment_update.html', {'form': form, 'enrollment': enrollment})

@login_required
def delete_enrollment(request, pk):
    """Delete enrollment with confirmation"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    print(enrollment)
    
    if enrollment:
        student_name = enrollment.student.name
        enrollment.delete()
        messages.success(request, f'Enrollment for {student_name} deleted successfully')
        return redirect('/software/enrollments/')
    
    # For GET request, should be handled by JavaScript modal
    return redirect('/software/enrollments/')













@login_required
def batch_list(request):
    """
    List all batches with filtering and statistics
    """
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    course_type_filter = request.GET.get('course_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    active_filter = request.GET.get('is_active', '')
    
    # Start with all batches
    batches = Batch.objects.all().order_by('-start_date')
    
    # Apply filters
    if search_query:
        batches = batches.filter(
            Q(batch_code__icontains=search_query) |
            Q(batch_title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        batches = batches.filter(batch_status=status_filter)
    
    if course_type_filter:
        if course_type_filter == 'basic':
            batches = batches.filter(basic_to_advance_cource__isnull=False)
        elif course_type_filter == 'advance':
            batches = batches.filter(advance_to_pro_cource__isnull=False)
    
    if active_filter:
        if active_filter == 'active':
            batches = batches.filter(is_active=True)
        elif active_filter == 'inactive':
            batches = batches.filter(is_active=False)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            batches = batches.filter(start_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            batches = batches.filter(start_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate statistics
    total_batches = batches.count()
    active_batches = batches.filter(is_active=True).count()
    upcoming_batches = batches.filter(batch_status='upcoming').count()
    ongoing_batches = batches.filter(batch_status='ongoing').count()
    completed_batches = batches.filter(batch_status='completed').count()
    
    # Total students across all batches
    total_students = sum(batch.current_students for batch in batches)
    
    # Total revenue from batches (sum of enrollment fees)
    total_revenue = Decimal('0.00')
    for batch in batches:
        batch_enrollments = batch.enrollments.all()
        for enrollment in batch_enrollments:
            total_revenue += enrollment.paid_amount
    
    # Add calculated properties to each batch for template
    for batch in batches:
        batch.display_current_students = batch.current_students
        batch.display_available_seats = batch.available_seats
        batch.display_occupancy = batch.occupancy_percentage
        batch.display_can_enroll = batch.can_enroll
        batch.display_duration = batch.duration_days
        batch.display_days_remaining = batch.days_remaining
        
        # Get course fees
        batch.display_fees = batch.course_fees
        
        # Get course title
        if batch.basic_to_advance_cource:
            batch.display_course_title = batch.basic_to_advance_cource.title
        elif batch.advance_to_pro_cource:
            batch.display_course_title = batch.advance_to_pro_cource.title
        else:
            batch.display_course_title = "No Course Assigned"
    
    # Pagination (10 items per page)
    paginator = Paginator(batches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare context
    context = {
        'batches': page_obj,
        
        # Statistics
        'total_batches': total_batches,
        'active_batches': active_batches,
        'upcoming_batches': upcoming_batches,
        'ongoing_batches': ongoing_batches,
        'completed_batches': completed_batches,
        'total_students': total_students,
        'total_revenue': total_revenue,
        
        # Filter values
        'search_query': search_query,
        'status_filter': status_filter,
        'course_type_filter': course_type_filter,
        'date_from': date_from,
        'date_to': date_to,
        'active_filter': active_filter,
        
        # Choices for filters
        'status_choices': Batch.BATCH_STATUS_CHOICES,
        'course_type_choices': [
            ('', 'All Types'),
            ('basic', 'Basic to Advance'),
            ('advance', 'Advance to Pro'),
        ],
        'active_choices': [
            ('', 'All'),
            ('active', 'Active Only'),
            ('inactive', 'Inactive Only'),
        ],
    }
    
    return render(request, 'batch_list.html', context)

@login_required
def create_batch(request):
    """Create new batch (opens in modal window)"""
    if request.method == 'POST':
        form = BatchForm(request.POST)
        
        if form.is_valid():
            try:
                batch = form.save(commit=True)
                messages.success(request, f'Batch "{batch.batch_code}" created successfully')
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error creating batch: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = BatchForm()
    
    return render(request, 'batch_create.html', {'form': form})

@login_required
def update_batch(request, pk):
    """Update existing batch (opens in modal window)"""
    batch = get_object_or_404(Batch, pk=pk)
    
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        
        if form.is_valid():
            try:
                batch = form.save(commit=True)
                messages.success(request, f'Batch "{batch.batch_code}" updated successfully')
                
                # Return JavaScript to close window
                return HttpResponse("""
                    <script>
                        if (window.opener && !window.opener.closed) {
                            window.opener.location.reload();
                        }
                        window.close();
                    </script>
                """)
            except Exception as e:
                messages.error(request, f'Error updating batch: {str(e)}')
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    
    else:
        form = BatchForm(instance=batch)
    
    return render(request, 'batch_update.html', {'form': form, 'batch': batch})

@login_required
def batch_detail(request, pk):
    """View batch details with enrolled students"""
    batch = get_object_or_404(Batch, pk=pk)
    
    # Get enrolled students
    enrollments = batch.enrollments.select_related('student').order_by('-enrollment_date')
    
    # Batch statistics
    total_students = batch.total_students
    current_students = batch.current_students
    completed_students = batch.enrollments.filter(status='completed').count()
    active_students = batch.enrollments.filter(status='active').count()
    
    # Payment statistics
    payments = []
    total_paid = Decimal('0.00')
    total_due = Decimal('0.00')
    
    for enrollment in enrollments:
        paid_amount = enrollment.paid_amount
        due_amount = enrollment.balance
        payments.append({
            'enrollment': enrollment,
            'paid': paid_amount,
            'due': due_amount
        })
        total_paid += paid_amount
        total_due += due_amount
    
    # Get course details
    course = batch.course
    course_details = {}
    if course:
        course_details = {
            'title': getattr(course, 'title', 'N/A'),
            'duration': getattr(course, 'duration', 'N/A'),
            'original_price': getattr(course, 'original_price', 'N/A'),
            'offer_price': getattr(course, 'offer_price', 'N/A'),
            'rating': getattr(course, 'rating', 'N/A'),
        }
    
    context = {
        'batch': batch,
        'enrollments': enrollments,
        'payments': payments,
        'total_students': total_students,
        'current_students': current_students,
        'completed_students': completed_students,
        'active_students': active_students,
        'total_paid': total_paid,
        'total_due': total_due,
        'course_details': course_details,
        'available_seats': batch.available_seats,
        'occupancy_percentage': batch.occupancy_percentage,
        'duration_days': batch.duration_days,
        'days_remaining': batch.days_remaining,
    }
    
    return render(request, 'batch_details.html', context)

@login_required
def delete_batch(request, pk):
    """Delete batch with confirmation"""
    batch = get_object_or_404(Batch, pk=pk)
    
    # Check if batch has enrollments
    if batch.enrollments.exists():
        messages.error(request, f'Cannot delete batch "{batch.batch_code}" because it has enrolled students.')
        return redirect(request.META.get('HTTP_REFERER', '/software/batches/'))
    
    if batch:
        batch_code = batch.batch_code
        batch.delete()
        messages.success(request, f'Batch "{batch_code}" deleted successfully')
        return redirect(request.META.get('HTTP_REFERER', '/software/batches/'))
    
    messages.info(request, 'Nothing to delete.')
    # For GET request, should be handled by JavaScript modal
    return redirect(request.META.get('HTTP_REFERER', '/software/batches/'))