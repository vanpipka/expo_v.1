from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from expo.DataSet import refreshLastOnline
from django.middleware import csrf
from django.dispatch import receiver

# Create your views here.
def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    token = csrf.get_token(request)

    print(token)
    print(request.COOKIES)

    return HttpResponse('Work Settings')


