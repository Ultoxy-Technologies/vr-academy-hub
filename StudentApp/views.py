from django.shortcuts import render,redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import mimetypes, os
from AdminApp.models import FreeCourse, FreeCourseProgress, Basic_to_Advance_Cource, Advance_to_Pro_Cource
from django.db.models import Sum
from functools import wraps

def is_student(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.role == 'is_student':
            return view_func(request, *args, **kwargs)
        # if not student → redirect to home
        if user.is_authenticated:
            if user.role=="is_student":
                return redirect('/student/dashboard')
            elif user.role=="is_staff":
                return redirect('/software/software-welcome-page')
            elif user.role=="is_crm_manager":
                return redirect('/staff/dashboard')
            elif user.is_superuser:
                return redirect('/admin/')
        else:
            messages.error(request,"Not sutable role found")
            return redirect('/')   # change 'home' if your url name is different
    return _wrapped_view


@is_student
@login_required
def student_dashboard(request):
    user = request.user
    # All progress records for the logged-in student
    progress_qs = FreeCourseProgress.objects.filter(student=user).select_related('course')

    # Total courses on platform (active ones)
    total_courses = FreeCourse.objects.filter(is_active=True).count()

    # Total watch time in seconds
    total_watch_time = progress_qs.aggregate(total=Sum('watched_duration'))['total'] or 0

    # Convert to hours/minutes (optional, for readability)
    total_watch_minutes = total_watch_time // 60
    total_watch_hours = total_watch_minutes // 60

    # Total watched videos (courses student has started)
    total_watched_videos = progress_qs.count()

    # Total certificates earned
    total_certificates = progress_qs.filter(
        completed=True, 
        course__certificate_template__isnull=False
    ).count()

    context = {
        'total_courses': total_courses,
        'total_watch_time': total_watch_time,
        'total_watch_minutes': total_watch_minutes,
        'total_watch_hours': total_watch_hours,
        'total_watched_videos': total_watched_videos,
        'total_certificates': total_certificates,
    }

    return render(request, 'student_dashboard.html', context)






@is_student
@login_required
def course_list(request):
    """
    Display list of free courses.
    """
    courses = FreeCourse.objects.all().order_by('-created_at').filter(is_active=True)
    return render(request, "free_course_list.html", {
        "courses": courses
    })


@is_student
@login_required
def basic_to_advance_course_list(request):
    """
    Display list of free courses.
    """
    courses = Basic_to_Advance_Cource.objects.all().order_by('-event_date').filter(is_active=True)
    return render(request, "basic_to_advance_course_list.html", {
        "courses": courses
    })


@is_student
@login_required
def advance_to_pro_course_list(request):
    """
    Display list of free courses.
    """
    courses = Advance_to_Pro_Cource.objects.all().order_by('-event_date').filter(is_active=True)
    return render(request, "advance_to_pro_course_list.html", {
        "courses": courses
    })



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

@is_student
@login_required
def free_course_video(request, course_id):
    course = get_object_or_404(FreeCourse, id=course_id)
    progress, _ = FreeCourseProgress.objects.get_or_create(student=request.user, course=course)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            watched_seconds = int(float(request.POST.get('watched_seconds', 0)))
            video_duration = int(float(request.POST.get('video_duration', 0)))
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "Invalid data"})

        # Cap watched_seconds so it never exceeds duration
        watched_seconds = min(watched_seconds, video_duration)

        # Save only if progress increased
        if watched_seconds > progress.watched_duration:
            progress.watched_duration = watched_seconds
            if watched_seconds >= video_duration:
                progress.mark_completed()
            else:
                progress.save(update_fields=["watched_duration"])

        return JsonResponse({
            "status": "success",
            "completed": progress.completed,
            "watched_duration": progress.watched_duration,
        })

    return render(request, "free_course_video.html", {
        "course": course,
        "progress": progress
    })

from django.contrib import messages

# @login_required
# def download_certificate(request, course_id):
#     """
#     Allow certificate download only if course is completed.
#     """
#     course = get_object_or_404(FreeCourse, id=course_id)
#     progress = get_object_or_404(FreeCourseProgress, student=request.user, course=course)

#     if not progress.completed or not course.certificate_template:
#         messages.error(request, "You must complete the course to download the certificate.")
#         # returen redirect to some page
#         return redirect(request.META.get('HTTP_REFERER', '/'))
    
#     certificate_path = course.certificate_template.path
#     file_name = os.path.basename(certificate_path)
#     mime_type, _ = mimetypes.guess_type(certificate_path)

#     with open(certificate_path, 'rb') as f:
#         response = HttpResponse(f.read(), content_type=mime_type)
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response



@is_student
@login_required
def download_certificate(request, course_id):
    """
    Allow certificate download only if course is completed.
    """ 
    course = get_object_or_404(FreeCourse, id=course_id)
    # progress = get_object_or_404(FreeCourseProgress, student=request.user, course=course)
    progress=FreeCourseProgress.objects.filter(student=request.user, course=course).first()
    if progress:
        if not progress.completed or not course.certificate_template:
            print("Function called")
            messages.error(request, "You must complete the course to download the certificate.") 
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            print("Function not called")
    else:
        print("Function called")
        messages.error(request, "You must complete the course to download the certificate.") 
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, 'cource_certificate.html', {'course': course})


@is_student
@login_required
def certificate_list(request):
    # Show only completed courses for this user
    progress_list = FreeCourseProgress.objects.filter(
        student=request.user, completed=True
    ).select_related('course')

    return render(request, 'certificate_list.html', {'progress_list': progress_list})