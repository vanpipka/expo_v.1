
from django.shortcuts import render
from datetime import datetime as datet
from datetime import timezone
from main.models import Company, News, JobOrder, UserType, Attacment, Message
from expo.DataSet import refreshLastOnline
from expo.DataGet import getCityListFull, getProfessionList
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json


# Create your views here.

def privacypolicy(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'PersonalData.html', {})

def forbiden(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/403.html', None, None, status='403')

def notfound(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/404.html', None, None, status='404')


def servererror(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/500.html', None, None, status='500')

def success(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    context = {'return_page': request.META.get('HTTP_REFERER', settings.HOME_PAGE)}

    print(context)

    return render(request, 'errors/success.html', context, None, status='200')

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

def savenews(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated and request.user.is_superuser:

        print(request.POST.__getitem__('data'))

        if request.method == "POST":

            if request.POST.__contains__('data'):

                print("Сохраняем новую новость")

                #{"name":"1","description":"3","link":"2"}
                data = dict(json.loads(request.POST.__getitem__('data')))

                status = News.SaveResponse(user = request.user, data = data)

            else:

                status = False

            if request.is_ajax():

                return HttpResponse(
                    json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                    status=200,
                    content_type='application/json')

            else:

                if status == True:
                    return HttpResponse(settings.HOME_PAGE + 'success/')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=403,
                        content_type='application/json')
            else:
                return render(request, 'errors/403.html', None, None, status=403)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)

def messages(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    messagelist = Message.GetAll(request.user)

    print(messagelist)

    return render(request, 'MessageList.html', {"messageList": messagelist})

def jobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)

        return render(request, 'JobList.html', {"jobsList": JobOrder.GetActual(JobOrder, user = request.user), "userType": userType, 'citylist': getCityListFull()})

    else:

        return render(request, 'errors/403.html', None, None, status='403')

def newjobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)

        return render(request, 'NewJob.html', {'userType': userType, 'citylist': getCityListFull(), 'professionsList': getProfessionList()})

    else:

        return render(request, 'errors/403.html', None, None, status=403)

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

                    if status == True:
                        return HttpResponse(settings.HOME_PAGE + 'success/')
                    else:
                        return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return render(request, 'errors/403.html', None, None, status=403)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)

def saveorder(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            if userType == 2:

                if request.POST.__contains__('data'):

                    #{"job_id": "96ca3684-c1cf-4641-b160-01124cfcdaff", "job_description": "444"}
                    data = dict(json.loads(request.POST.__getitem__('data')))

                    status = JobOrder.SaveOrder(user=request.user, data = data)

                else:

                    status = False

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                        status=200,
                        content_type='application/json')

                else:

                    print("сохраняем заявку" + str(status))

                    if status == True:
                        return HttpResponse(settings.HOME_PAGE + 'success/')
                    else:
                        return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)
            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return render(request, 'errors/404.html', None, None, status=404)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)