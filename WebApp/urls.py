from django.urls import path
from .views import *
urlpatterns = [
    path('', index, name='index'),
    path('gallary-images', web_photos_gallary, name='photo_gallery'),
    path('gallary-videos', web_videos_gallary, name='video_gallery'),
    path('about-us', about_us, name='about_us'),
    path('free_cources', free_cources, name='free_cources'),
    path('basic-to-advance', basic_to_advance, name='basic_to_advance'),
    path('advance-to-pro', advance_to_pro, name='advance_to_pro'),
    path('awards-recognition', awards, name='awards'),
    path('trusted-broker', trusted_broker, name='trusted_broker'),
    path('contact-us', contct_us, name='contact_us'), 
    
    
]
