from django.shortcuts import render, redirect
from AdminApp.models import PasswordResetOTP,PhotoGalleryCategories,EventRegistration, PhotoGallery, VideoGallery,FreeCourse,Basic_to_Advance_Cource,Advance_to_Pro_Cource,Certificate,Event
from django.contrib import messages
from AdminApp.models import Enquiry
import threading
from django.core.mail import EmailMessage

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')



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




from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from datetime import datetime
import threading


# --- Function to send email in background ---
def send_email_in_background(email_message):
    try:
        email_message.send()
    except Exception as e:
        print(f"Error sending email: {e}")


# --- Contact Form View ---
def contact_us(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message_text = request.POST.get("message", "").strip()

        # Basic validation
        if not all([name, phone, email, message_text]):
            messages.error(request, "All fields are required.")
            return redirect("/contact-us")

        # Save to database
        enquiry = Enquiry.objects.create(
            full_name=name,
            phone=phone,
            email=email,
            message=message_text
        )

        # Send email notification
        try:
            subject = "📩 New Enquiry Received from Website"
            current_datetime = datetime.now().strftime("%d %B %Y, %I:%M %p")

            # Render HTML email template with enquiry data
            email_body = render_to_string('Enquiry_Mail.html', {
                'full_name': name,
                'phone': phone,
                'email': email,
                'message': message_text,
                'submitted_on': current_datetime
            })

            email_message = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['prameshwar4378@gmail.com'],  # Change to admin or target email
            )
            email_message.content_subtype = 'html'

            # Send asynchronously
            threading.Thread(target=send_email_in_background, args=(email_message,)).start()

            messages.success(request, "Thank you! Your enquiry has been submitted successfully.")
            return redirect("/contact-us")

        except Exception as e:
            print(f"Email Error: {e}")
            messages.error(request, "Your enquiry was saved, but email notification failed.")
            return redirect("/contact-us")

    # GET request → render contact form
    return render(request, 'contact_us.html')



# def contact_us_mail(request):
#     try:
#         # Prepare the subject
#         email_subject = "New Contact Us Enquiry Received"
#         current_datetime = datetime.now()
 
#         # Render email content
#         email_body = render_to_string('enquiry_mail-templates.html', )

#         # Configure the email
#         email_message = EmailMessage(
#             subject=email_subject,
#             body=email_body,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=['prameshwar4378@gmail.com'],  # Replace with the appropriate email address
#         )
#         email_message.content_subtype = 'html'

#         # Send the email in a background thread
#         email_thread = threading.Thread(target=send_email_in_background, args=(email_message,))
#         email_thread.start()

#         messages.success(request,"Contact US email sent successfully.")
#         return redirect('/contact_us')
     
#     except Exception as e:
#         messages.error(request,f"Error in Enquiry: {e}")
#         return redirect('/contact_us')




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


# --- Register User View ---
def register_user(request):
    # If user already logged in, redirect
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect('/student/dashboard')

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Display success message
            messages.success(request, "Registration successful. You can now log in.")

            # Prepare and send email
            try:
                subject = "🧾 New User Registration - Ultoxy Technologies"
                current_datetime = datetime.now().strftime("%d %B %Y, %I:%M %p")

                # Render HTML email with user data
                email_body = render_to_string('New_Registration_Mail.html', {
                    'name': user.name,
                    'dob': user.dob,
                    'dist': user.dist,
                    'taluka': user.taluka,
                    'village': user.village,
                    'mobile_number': user.mobile_number,
                    'email': user.email,
                    'registered_on': current_datetime,
                })

                email_message = EmailMessage(
                    subject=subject,
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['ultoxy.tech@gmail.com',f'{user.email}'],  # Admin/notification email
                )
                email_message.content_subtype = 'html'

                # Send in background
                threading.Thread(target=send_email_in_background, args=(email_message,)).start()

            except Exception as e:
                print(f"Email Error: {e}")
                messages.warning(request, "User registered, but email notification failed.")

            return redirect('/')  # Redirect to login/home page
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = CustomUserForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import datetime
import threading  # ✅ Added for background email sending

User = get_user_model()

# --- Helper Function for Sending Email in Background ---
def send_password_forgat_email_in_background(subject, message, from_email, recipient_list):
    """Send email asynchronously in a background thread (supports HTML)."""

    def send_async():
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
            )
            email.content_subtype = "html"  # ✅ ensure email renders HTML properly
            email.send(fail_silently=False)
            print(f"✅ Email sent successfully to {recipient_list[0]} in background.")
        except Exception as e:
            print(f"❌ Error sending email: {e}")

    threading.Thread(target=send_async).start()  # run in background thread




    threading.Thread(target=send_async).start()
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime

# --- Password Reset View ---
def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        try:
            user = User.objects.get(email=email)

            # Generate new OTP
            otp = PasswordResetOTP.generate_otp()
            PasswordResetOTP.objects.create(user=user, otp=otp)

            # Email content
            subject = "Your Password Reset OTP - VR Academy Hub"
            message = f"""
            <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 40px 0;">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" 
                       style="max-width: 600px; background-color: #ffffff; border-radius: 10px; 
                              overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                    <tr>
                        <td align="center" style="background-color: #2c7be5; padding: 20px 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">VR Academy Hub</h1>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 30px; color: #333333;">
                            <p style="font-size: 16px;">Hello <strong>{user.name}</strong>,</p>

                            <p style="font-size: 15px; line-height: 1.6;">
                                We received a request to reset your password. Please use the One-Time Password (OTP) below to proceed:
                            </p>

                            <p style="text-align: center; margin: 30px 0;">
                                <span style="display: inline-block; font-size: 28px; font-weight: bold; color: #2c7be5; 
                                            background-color: #eef5ff; padding: 15px 40px; border-radius: 8px; 
                                            letter-spacing: 3px;">
                                    {otp}
                                </span>
                            </p>

                            <p style="font-size: 14px; color: #555;">
                                This code is valid for <strong>10 minutes</strong>.
                            </p>

                            <p style="font-size: 14px; color: #555;">
                                Your username: <strong>{user.mobile_number}</strong>
                            </p>

                            <p style="font-size: 13px; color: #888; margin-top: 25px;">
                                If you did not request this password reset, please ignore this message. Your account remains secure.
                            </p>

                            <p style="margin-top: 35px; font-size: 14px; color: #333;">
                                Best regards,<br>
                                <em>The Support Team</em><br>
                                <strong>VR Academy Hub</strong>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <td align="center" style="background-color: #f1f3f5; padding: 15px; font-size: 12px; color: #999;">
                            © {datetime.now().year} VR Academy Hub. All rights reserved.
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # ✅ Send email in background (non-blocking & HTML formatted)
            send_password_forgat_email_in_background(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            messages.success(request, f"OTP has been sent to {email}")
            print("✅ OTP sent successfully to email (in background).")

            # Redirect to reset password page
            return redirect(f"/reset-password/?email={email}")

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email.')
            print("❌ No user found with this email.")
            return render(request, 'request_password_reset.html')

    return render(request, 'request_password_reset.html')




def reset_password_with_otp(request):
    print("Reset Password with OTP called.")
    email = request.GET.get('email') or request.POST.get('email')

    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()

        try:
            user = User.objects.get(email=email)
            otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

            if not otp_entry:
                print("Invalid OTP entered.")
                messages.error(request, 'Invalid OTP. Please check your email and try again.')
                return render(request, 'reset_password.html', {'email': email})

            if not otp_entry.is_valid():
                print("OTP has expired.")
                messages.error(request, 'OTP expired. Please request a new one.')
                return redirect('/forgot-password/')

            # ✅ OTP valid → reset password
            user.set_password(new_password)
            user.save()
            otp_entry.delete()

            print("✅ Password reset successfully.")
            messages.success(request, 'Your password has been reset successfully. You can now log in.')
            return redirect('/login/')  # change to your actual login route

        except User.DoesNotExist:
            print("❌ No user found with this email.")
            messages.error(request, 'No user found with this email.')
            return redirect('/forgot-password/')

    return render(request, 'reset_password.html', {'email': email})


from django.shortcuts import render, get_object_or_404 

def event_detail(request, event_id):
    """
    Display the full details of a single event.
    """
    event = get_object_or_404(Event, id=event_id) 

    context = {
        'event': event,
         'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'save_amount': event.registration_strickthrough_fee - event.registration_offer_fee if event.registration_strickthrough_fee else 0
    
    }
    return render(request, 'event_detail.html', context)



import razorpay
import json
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone 
from .forms import EventRegistrationForm

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Set up logging
logger = logging.getLogger(__name__)

def event_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id, status='published')
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create registration record
                registration = form.save(commit=False)
                registration.event = event
                
                # Generate registration ID before saving
                if not registration.registration_id:
                    registration.registration_id = registration.generate_registration_id()
                
                if event.is_free:
                    # Free event - no payment required
                    registration.payment_status = 'success'
                    registration.save()
                    logger.info(f"Free registration created: {registration.registration_id}")
                    return redirect('registration_success', registration_id=registration.registration_id)
                else:
                    # Paid event - create Razorpay order
                    registration.save()
                    logger.info(f"Creating Razorpay order for registration: {registration.registration_id}")
                    
                    # Create Razorpay order with string values
                    order_data = {
                        'amount': event.current_price,  # amount in paisa
                        'currency': 'INR',
                        'receipt': str(registration.registration_id),  # Convert to string
                        'notes': {
                            'event_id': str(event.id),  # Convert to string
                            'registration_id': str(registration.registration_id),  # Convert to string
                        }
                    }
                    
                    try:
                        order = client.order.create(data=order_data)
                        registration.razorpay_order_id = order['id']
                        registration.save()
                        
                        logger.info(f"Razorpay order created: {order['id']}")
                        
                        return render(request, 'payment.html', {
                            'event': event,
                            'registration': registration,
                            'order': order,
                            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                            'callback_url': request.build_absolute_uri('/payment/verify/'),
                        })
                        
                    except Exception as e:
                        logger.error(f"Razorpay order creation failed: {str(e)}")
                        registration.payment_status = 'failed'
                        registration.save()
                        form.add_error(None, f'Payment initialization failed: {str(e)}')
            
            except Exception as e:
                logger.error(f"Registration creation failed: {str(e)}")
                form.add_error(None, f'Registration failed: {str(e)}')
    
    else:
        form = EventRegistrationForm()
    
    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'event_registration.html', context)

@csrf_exempt
def payment_verification(request):
    if request.method == "POST":
        try:
            # Get payment details from request
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            logger.info(f"Payment verification started for order: {razorpay_order_id}")
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify signature
            client.utility.verify_payment_signature(params_dict)
            
            # Signature verification successful
            registration = EventRegistration.objects.get(razorpay_order_id=razorpay_order_id)
            registration.razorpay_payment_id = razorpay_payment_id
            registration.razorpay_signature = razorpay_signature
            registration.payment_status = 'success'
            registration.save()
            
            logger.info(f"Payment successful for registration: {registration.registration_id}")
            
            return redirect('registration_success', registration_id=registration.registration_id)
            
        except EventRegistration.DoesNotExist:
            logger.error(f"Registration not found for order: {razorpay_order_id}")
            return JsonResponse({'status': 'error', 'message': 'Registration not found'})
        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Invalid payment signature for order: {razorpay_order_id} - {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Invalid payment signature'})
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def create_razorpay_order(request, event_id):
    """API endpoint to create Razorpay order"""
    if request.method == "POST":
        try:
            event = get_object_or_404(Event, id=event_id)
            
            # Generate a temporary receipt ID
            temp_receipt = f"temp_{int(timezone.now().timestamp())}"
            
            order_data = {
                'amount': event.current_price,
                'currency': 'INR',
                'receipt': temp_receipt,  # Use string receipt
                'notes': {
                    'event_id': str(event.id),  # Convert to string
                }
            }
            
            order = client.order.create(data=order_data)
            logger.info(f"Razorpay order created via API: {order['id']}")
            return JsonResponse({'order_id': order['id']})
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed via API: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

def registration_success(request, registration_id):
    registration = get_object_or_404(EventRegistration, registration_id=registration_id)
    
    context = {
        'registration': registration,
        'event': registration.event,
    }
    return render(request, 'registration_success.html', context)