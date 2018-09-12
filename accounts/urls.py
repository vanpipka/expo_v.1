# chat/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup_worker),
    path('signup_company/', views.signup_company),
    path('login/', views.Login),
    path('logout/', views.Logout),
]