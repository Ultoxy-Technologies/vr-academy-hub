from django.shortcuts import render, redirect
from AdminApp.models import PhotoGalleryCategories, PhotoGallery, VideoGallery
from django.contrib import messages
from AdminApp.models import Enquiry

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')


# Course Level pages
def free_cources(request):
    return render(request, 'free_cources.html')


def basic_to_advance(request):
    return render(request, 'basic_to_advance.html')

def advance_to_pro(request):
    return render(request, 'advance_to_pro.html')

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
def awards(request):
    return render(request, 'awards.html')

# Our Trusted Broker
def trusted_broker(request):
    return render(request, 'trusted_broker.html')

# Contact Us page
def contact(request):
    return render(request, 'contact.html')

from .forms import CustomUserForm, CustomUserLoginForm
from django.contrib.auth import login

def register_user(request):
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
