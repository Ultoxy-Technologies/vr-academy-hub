"""
URL configuration for VRACADEMYHUB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from WebApp import urls as web_urls
from StudentApp import urls as student_urls
from SoftwareApp import urls as software_urls

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    # 🌐 Language switching endpoint
    path('i18n/', include('django.conf.urls.i18n')),
]

# 🌍 Add language-based URL patterns (this allows URLs like /en/, /hi/, /mr/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include(web_urls)),
    path('student/', include(student_urls)),
    path('software/', include(software_urls)),

    # Your custom auth routes preserved
    path('register/', web_urls.register_user, name='register_user'),
    path('login/', web_urls.login_user, name='login'),
    path('logout/', web_urls.logout, name='logout'),
)

# 📁 Serve media files in development
# 📁 Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
