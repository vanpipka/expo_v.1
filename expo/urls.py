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
from expo import views

urlpatterns = [
    path('adminexpo/workers/', views.adminexpoworkers),
    path('adminexpo/comments/', views.adminexpocomments),
    path('adminexpo/companys/', views.adminexpocompanys),
    path('adminexpo/save/', views.adminexposave),
    path('adminexpo/', views.adminexpo),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('main.urls')),
    path('worker/', include('worker.urls')),
    path('forbiden/', views.forbiden),
    path('notfound/', views.notfound),
    path('servererror/', views.servererror),
    path('success/', views.success),
    path('privacy-policy/', views.privacypolicy),
    path('company/', views.company),
    path('messages/', views.messages),
    path('news/save/', views.savenews),
    path('news/', views.news),
    path('jobs/save/', views.savejobs),
    path('jobs/saveorder/', views.saveorder),
    path('jobs/new/', views.newjobs),
    path('jobs/', views.jobs),
    path('sendsms/', views.sendsms),
]


