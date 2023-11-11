"""
URL configuration for kenar_sample_addon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from .views import landing, start_verification, oauth_callback, form, verify

urlpatterns = [
    path("landing/", landing, name="landing"),
    path("start/", start_verification, name="start"),
    path("oauth-callback/", oauth_callback, name="oauth-callback"),
    path("form/", form, name="form"),
    path("verify/", verify, name="verify"),
]

app_name = 'kenar_sample_addon.background_check'
