from django.shortcuts import render, redirect
from AdminApp.models import PhotoGalleryCategories, PhotoGallery, VideoGallery,FreeCourse,Basic_to_Advance_Cource,Advance_to_Pro_Cource,Certificate
from django.contrib import messages
from AdminApp.models import Enquiry
import threading
from django.core.mail import EmailMessage

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')


def send_email_in_background(email_message):
    try:
        email_message.send()
    except Exception as e:
        print(f"Error sending email: {e}")


# Course Level pages
def free_cources(request):
    courses = FreeCourse.objects.filter(is_active=True)
    return render(request, 'free_cources.html', {'courses': courses})


def basic_to_advance(request):
    courses = Basic_to_Advance_Cource.objects.filter(is_active=True)
    return render(request, 'basic_to_advance.html', {'courses': courses})

def advance_to_pro(request):
    courses = Advance_to_Pro_Cource.objects.filter(is_active=True)
    return render(request, 'advance_to_pro.html', {'courses': courses})

def contct_us(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        # Basic validation
        if not name or not phone or not email or not message:
            messages.error(request, "All fields are required.")
        else:
            # Save to database
            Enquiry.objects.create(
                full_name=name,
                phone=phone,
                email=email,
                message=message
            )
            messages.success(request, "Thank you! Your enquiry has been submitted.")
            return redirect("/contact-us")  # redirect to the same page

    return render(request, 'contct_us.html')


def contact_us_mail(request):
    try:
        # Prepare the subject
        email_subject = "New Enquiry Recerived from Website"
        current_datetime = datetime.now()
 
        # Render email content
        email_body = render_to_string('Enquiry_Mail.html', )

        # Configure the email
        email_message = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['prameshwar4378@gmail.com'],  # Replace with the appropriate email address
        )
        email_message.content_subtype = 'html'

        # Send the email in a background thread
        email_thread = threading.Thread(target=send_email_in_background, args=(email_message,))
        email_thread.start()

        messages.success(request,"Enquiry Alert email sent successfully.")
        return redirect('/contact_us')
     
    except Exception as e:
        messages.error(request,f"Error in Enquiry Alert email: {e}")
        return redirect('/contact_us')
    
 

def contact_us_mail(request):
    try:
        # Prepare the subject
        email_subject = "New Contact Us Enquiry Received"
        current_datetime = datetime.now()
 
        # Render email content
        email_body = render_to_string('enquiry_mail-templates.html', )

        # Configure the email
        email_message = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['prameshwar4378@gmail.com'],  # Replace with the appropriate email address
        )
        email_message.content_subtype = 'html'

        # Send the email in a background thread
        email_thread = threading.Thread(target=send_email_in_background, args=(email_message,))
        email_thread.start()

        messages.success(request,"Contact US email sent successfully.")
        return redirect('/contact_us')
     
    except Exception as e:
        messages.error(request,f"Error in Enquiry: {e}")
        return redirect('/contact_us')




def web_photos_gallary(request): 
    categories = PhotoGalleryCategories.objects.prefetch_related('photos').all()
    return render(request, "web_photos_gallary.html", {'categories': categories})

 
import re

def extract_video_id(embed_url):
    match = re.search(r"embed/([a-zA-Z0-9_-]+)", embed_url)
    if match:
        return match.group(1)
    return None


def web_videos_gallary(request): 
    data = VideoGallery.objects.all()
    video_data=[]
    for embed_link in data:
        embed_url= embed_link.video_link
        if embed_url:
            video_id=extract_video_id(embed_url)
        
            if video_id:
                video_data.append(
                    {"thumbnail_url":f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "video_url":f"https://www.youtube.com/embed/{video_id}",
                    "id":embed_link.id} 
                )
  
    return render(request, 'web_video_gallary.html', {"video_data":video_data})




# Awards & Recognition
def certificates(request):
    certificates = Certificate.objects.filter(is_active=True).order_by('-issue_date')
    return render(request, 'certificates.html', {'certificates': certificates})


# Our Trusted Broker
def trusted_broker(request):
    return render(request, 'trusted_broker.html')

# Contact Us page
def contact(request):
    return render(request, 'contact.html')

from .forms import CustomUserForm, CustomUserLoginForm
from django.contrib.auth import login

def register_user(request):
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect('/student/dashboard')  
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")   
            return redirect('/')  # redirect to login page after successful registration
    else:
        form = CustomUserForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('/student/dashboard')  # or any page
        else:
            messages.error(request, "Invalid mobile number or password.")
    else:
        form = CustomUserLoginForm()
    
    return render(request, 'login.html',{'form': form})

from django.contrib.auth import logout as DeleteSession

def logout(request):
    DeleteSession(request)
    return redirect('/login')
