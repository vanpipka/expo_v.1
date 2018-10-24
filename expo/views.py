
from django.shortcuts import render
from datetime import datetime as datet
from datetime import timezone
from main.models import Company, News, JobOrder, UserType, Attacment
from expo.DataSet import refreshLastOnline
from expo.DataGet import getCityListFull, getProfessionList
from django.http import HttpResponseForbidden, Http404, HttpResponse, JsonResponse
import json


# Create your views here.
def company(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    companyList = []

    query = Company.objects.all()

    for e in query:
        companyList.append({'name': e.name,
                'id': e.id,
                'fotourl': Attacment.getlink(e.image),
                'resizefotourl': Attacment.getresizelink(e.image),
                'isonline': True if (datet.now(timezone.utc) - e.lastOnline).seconds / 60 < 5 else False,
                'lastonline': e.lastOnline,
                'description': e.description
               })

    return render(request, 'CompanyList.html', {"companyList": companyList})

def news(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'NewsList.html', {"newsList": News.GetActual(News)})

def jobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)

        return render(request, 'JobList.html', {"jobsList": JobOrder.GetActual(JobOrder, user = request.user), "userType": userType, 'citylist': getCityListFull()})

    else:

        return HttpResponseForbidden()

def newjobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)

        return render(request, 'NewJob.html', {'userType': userType, 'citylist': getCityListFull(), 'professionsList': getProfessionList()})

    else:

        return HttpResponseForbidden()

def savejobs(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            print('тип юзера: ' + str(userType))

            if userType == 1:

                if request.POST.__contains__('data'):

                    print("Сохраняем отклик")

                    print(request.POST.__getitem__('data'))

                    #{"job_id": "96ca3684-c1cf-4641-b160-01124cfcdaff", "job_description": "444"}
                    data = dict(json.loads(request.POST.__getitem__('data')))

                    status = JobOrder.SaveResponse(user = request.user, data = data)

                else:

                    status = False

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                        status=200,
                        content_type='application/json')

                else:

                    return HttpResponse('/jobs/')

            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse('Что то пошло не так')

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return Http404()
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return HttpResponseForbidden()

def saveorder(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            print('тип юзера: ' + str(userType))

            if userType == 2:

                if request.POST.__contains__('data'):

                    #{"job_id": "96ca3684-c1cf-4641-b160-01124cfcdaff", "job_description": "444"}
                    data = dict(json.loads(request.POST.__getitem__('data')))

                    status = JobOrder.SaveOrder(user = request.user, data = data)

                else:

                    status = False

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                        status=200,
                        content_type='application/json')

                else:

                    return HttpResponse('/jobs/')

            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse('Что то пошло не так')

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return Http404()
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return HttpResponseForbidden()