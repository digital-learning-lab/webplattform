"""dll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import path, include

from dll.content.views import HomePageView, ImprintView, DataPrivacyView, StructureView, UsageView, DevelopmentView, \
    NewsletterRegisterView, NewsletterUnregisterView, ContactView, ToolDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('impressum', ImprintView.as_view(), name='imprint'),
    path('datenschutz', DataPrivacyView.as_view(), name='data-privacy'),
    path('struktur', StructureView.as_view(), name='structure'),
    path('nutzung', UsageView.as_view(), name='usage'),
    path('entwicklung', DevelopmentView.as_view(), name='development'),
    path('newsletter', NewsletterRegisterView.as_view(), name='newsletter'),
    path('newsletter/abmelden', NewsletterUnregisterView.as_view(), name='newsletter-unregister'),
    path('kontakt', ContactView.as_view(), name='contact'),
    path('faq', views.flatpage, {'url': '/faq/'}, name='faq'),
    path('tools/<slug:slug>', ToolDetailView.as_view(), name='tool-detail'),
    # path('', include('django.contrib.flatpages.urls')),
    path('', include('dll.user.urls', namespace='user'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)