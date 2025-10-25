from django.shortcuts import render
from AdminApp.models import PhotoGalleryCategories, PhotoGallery, VideoGallery
# Create your views here.
def index(request):
    return render(request, 'index.html')
def about_us(request):
    return render(request, 'about_us.html')


# Course Level pages
def basic_to_advance(request):
    return render(request, 'basic_to_advance.html')

def advance_to_pro(request):
    return render(request, 'advance_to_pro.html')


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