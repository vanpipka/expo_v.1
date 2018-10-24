"""expo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path , include
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('', views.show),
    path('m/servicelist/', views.jsonServicesList),
    path('m/selectionparameters/', views.jsonSelectionParameters),
    path('m/citylist/', views.jsonCityList),
    path('m/countrylist/', views.jsonCountryList),
    path('m/checklogin/', views.checkLogin),
    path('m/checkserver/', views.checkServer),
    path('m/professionlist/', views.jsonProfessionList),
    path('m/professionandgroups/', views.showJson),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()