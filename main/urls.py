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
from django.urls import path, include
from . import views
from expo.views import notfound
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

#handler404 = notfound

urlpatterns = [
    path('', views.show),
    path('sendlink/', views.sendlink),
    path('m/servicelist/', views.jsonServicesList),
    #path('m/servicelist/save/', views.ServicesListSave),
    path('m/selectionparameters/', views.jsonSelectionParameters),
    path('m/citylist/', views.jsonCityList),
    path('m/citylistgroup/', views.jsonCityListGroup),
    path('m/countrylist/', views.jsonCountryList),
    path('m/checklogin/', views.checkLogin),
    path('m/checkserver/', views.checkServer),
    path('m/professionlist/', views.jsonProfessionList),
    path('m/fiolist/', views.jsonFioList),
    #path('m/professionlist/save/', views.ProfessionsListSave),
    path('m/professionandgroups/', views.showJson),
    path('m/companies/', views.jsonCompanyList)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
