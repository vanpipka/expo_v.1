"""djangotest URL Configuration

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
from django.urls import path
from . import views

urlpatterns = [
    path('settings/save/', views.saveSettings),
    path('settings/', views.showSettings),
    path('m/settings/', views.showSettingsJson),
    path('search/', views.showSearch),
    path('searchnext/', views.showWorkersList),
    path('info/', views.showWorker),
    path('m/info/', views.showWorkersJson),
    path('m/search/', views.showSearchJson),
    path('comments/save/', views.saveComments),
    path('m/comments/', views.showCommentsJson),
    path('testcsrf/', views.my_view),
    path('searchtest/', views.showSearchTest),
]
