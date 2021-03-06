# chat/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup_worker),
    path('signup_change/', views.signup_change),
    path('signup_company/', views.signup_company),
    path('login/', views.Login),
    path('loginexpo/', views.LoginExpo),
    path('logout/', views.Logout),
    path('reset/', views.Reset),
]