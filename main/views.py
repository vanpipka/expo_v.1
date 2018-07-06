from django.http import HttpResponse , JsonResponse
from django.shortcuts import render, redirect
from expo.DataGet import getProfessionListWithGroup, getProfessionList, getAllProfessionsAndGroups
from expo.DataSet import refreshLastOnline
# Create your views here.

def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getAllProfessionsAndGroups(count=5)
    return render(request, 'index.html', context)

def jsonServicesList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getProfessionList()

    response = JsonResponse({'professionList': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def showJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getAllProfessionsAndGroups()

    return JsonResponse(context)


