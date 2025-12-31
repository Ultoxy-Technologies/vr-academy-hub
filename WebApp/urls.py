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
    path('certificates/', certificates, name='certificates'),
    path('trusted-broker', trusted_broker, name='trusted_broker'),
    path('contact-us', contact_us, name='contact_us'), 
    path('forgot-password/', request_password_reset, name='forgot_password'),
    path('reset-password/', reset_password_with_otp, name='reset_password'),
    
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', event_registration, name='event_registration'),
    path('payment/verify/', payment_verification, name='payment_verification'),
    path('registration/success/<str:registration_id>/', registration_success, name='registration_success'),
    path('create-order/<int:event_id>/', create_razorpay_order, name='create_order'),

    path('events/', event_list, name='event_list'),
    
]
