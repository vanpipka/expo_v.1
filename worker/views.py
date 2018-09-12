from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from main.models import Comments, Worker, Professions, UserType, Company
from main.forms import CommentForm
from expo.DataGet import getComments, getProfessionListWithGroup, getServiceList, gerWorkList, searchWorker, getCityList, getCityListFull, getCountryList
from expo.DataSet import setWorker, refreshLastOnline
from django.views.decorators.csrf import csrf_exempt
from django.middleware import csrf
from django.contrib.auth.models import User
import json


# Create your views here.
def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    return HttpResponse('Work Settings')

def saveSettings(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            print('тип юзера: ' + str(userType))

            if userType == 1:

                #print("СОХРАНЯЕМ НАСТРОЙКИ SAVE================================================================================")
                #print(request.read())
                #print(request.FILES)
                #print(request.POST)
                #
                #print("================================================================================")

                if request.POST.__contains__('data'):

                    print("Сохраняем рабочего")

                    print(request.POST.__getitem__('data'))

                    data = dict(json.loads(request.POST.__getitem__('data')))

                    setWorker(request.user, data)

                return HttpResponse('http://py.itoe.ru:56503/worker/settings/')

            elif userType == 2:

                if request.POST.__contains__('data'):

                    print("Сохраняем компанию")

                    print(request.POST.__getitem__('data'))

                    data = dict(json.loads(request.POST.__getitem__('data')))

                    Company.UpdateCompany(user=request.user, data=data)

                return HttpResponse('http://py.itoe.ru:56503/worker/settings/')

            else:

                HttpResponse('Что то пощло не так')

        else:

            return HttpResponse('404: Страница не найдена')
    else:
        return HttpResponse('403: Доступ запрещен')

def showSettings(request):

    #Эта страница используется только для отображения настроек сохранение через settings/save/

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        userType = UserType.GetUserType(request.user)

        print('тип юзера: '+str(userType))

        if userType == 1:

            worker          = gerWorkList(user_id=request.user, userAauthorized=request.user.is_authenticated, itsSettings=True)
            selectedList    = []

            if worker != None and len(worker) > 0:
                worker          = worker[0]
                selectedList    = worker.get('proflist')
            else:
                worker          = {}

            context = {'worker': worker,
                       'city': getCityList(),
                       'citylist': getCityListFull(),
                       'serviceList': getServiceList(),
                       'countryList': getCountryList(),
                       'professionList': getProfessionListWithGroup(selectedList=selectedList)}
            print("Ответ:")
            print(worker)

            return render(request, 'WorkerSettings.html', context)

        elif userType == 2:

            company = Company.GetCompanyByUser(user=request.user)

            context = {'company': company, 'citylist': getCityListFull()}

            return render(request, 'CompanySettings.html', context)

        else:
            return HttpResponse('Что то пошло не так')
    else:
        return HttpResponse('403: Доступ запрещен')

def showSettingsJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    print('Настройки: ' + str(request.POST))

    print('showSettingsJson куки:' + str(request.COOKIES))

    print('Настройки: '+ str(request.user))

    if request.user.is_authenticated:

        token = csrf.get_token(request)

        worker          = gerWorkList(user_id=request.user, userAauthorized=request.user.is_authenticated, itsSettings=True)
        selectedList    = []

        if worker != None and len(worker) > 0:
            worker          = worker[0]
            selectedList    = worker.get('proflist')
        else:
            worker          = {"name": "", "surname": "", "lastname":""}

        context = {'worker': worker,
                       #'city': getCityList(),
                       #'serviceList': getServiceList(),
                       'professionList': getProfessionListWithGroup(selectedList=selectedList),
                       'csrfmiddlewaretoken': token}

        #return render(request, 'WorkerSettings.html', context)
    else:
        context["message"] = '403: Доступ запрещен'

    return JsonResponse(context)

def showWorker(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    id = request.GET.get("id", None)

    if id == None:

        return render(request, 'SearchWorker.html', {})

    if request.method == "GET":

        commentForm = CommentForm()

    workerList = gerWorkList(idWorker=[id], userAauthorized=userAauthorized)
    comments = Comments.objects.filter(idWorker=id).order_by("-created")[:10]

    print("Ответ:" + str(len(workerList)))
    return render(request, 'Worker.html', {"worker": workerList[0], "commentForm": commentForm, "comments": comments, "userAauthorized": userAauthorized})

def showWorkersJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    profession  = None
    id          = None

    print('Запрос: ' + str(request.POST))
    print('Куки: ' + str(request.COOKIES))

    if request.method == "GET":
        profession = request.GET.get("profession", None)
        id = request.GET.get("id", None)

        if id != None:  #пока так
            id = [id]

    context = {}
    context["dataset"] = gerWorkList(idGroup=profession, idWorker=id, userAauthorized=request.user.is_authenticated, groupAttribute = True)

    return JsonResponse(context)

def showSearchJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    print(request.POST)

    if request.method == "POST":

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        print('шоу серч: '+ str(dictPost))
        context = searchWorker(searchList=dictPost, groupAttribute=True)

    elif request.method == "GET":

        category    = request.GET.get("profession", "")
        city        = request.GET.get("city", "")

        context = searchWorker(searchList={'Profession': [category], 'City': [city]}, userAauthorized=request.user.is_authenticated, groupAttribute=True)

    return JsonResponse(context)

def showSearch(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    print("Попали")

    if request.method == "POST":

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(searchList=dictPost)

    elif request.method == "GET":

        category    = request.GET.get("profession", '')
        city        = request.GET.get("city", '')

        context = searchWorker(searchList={'profession': category, 'city': city}, userAauthorized=request.user.is_authenticated)

    context["count"] = len(context.get('dataset'))
    context['citylist'] = getCityListFull()
    context['servicelist'] = getServiceList()

    return render(request, 'SearchWorker.html', context)

def showWorkersList(request):

    context = {}

    if request.method == "POST":
        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(searchList=dictPost)

        context["count"] = len(context.get('dataset'))

    return render(request, 'includes/WorkerList.html', context);

def showSearchTest(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {"count": 0}

    if request.method == "POST":

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(searchList=dictPost, userAauthorized = request.user.is_authenticated, returnCount = True)

    return JsonResponse(context)

def showCommentsJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {"dataset":[]}

    if request.method == "GET":
        userid = request.GET.get("userid", "")

        if userid != "":
            context["dataset"] = getComments(idUser=userid)

    context['csrfmiddlewaretoken'] = csrf.get_token(request)

    return JsonResponse(context)

def saveComments(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:
        if request.method == "POST":

            if request.POST.__contains__('data'):

                data = dict(json.loads(request.POST.__getitem__('data')))

                Comment = Comments()

                Comment.idUser   = request.user.usertype.worker
                Comment.idWorker = get_object_or_404(Worker, id=data.get("idworker"))
                Comment.text     = data.get("text")
                Comment.rating   = data.get("rating")
                Comment.idProf   = get_object_or_404(Professions, id=data.get("idprofession"))
                Comment.save()

                return HttpResponse("http://py.itoe.ru:56503/worker/info/?id=" + str(data.get("idworker")))

            return HttpResponse('http://py.itoe.ru:56503/')

        else:

            return HttpResponse('404: Страница не найдена')
    else:
        return HttpResponse('403: Доступ запрещен')

@csrf_exempt
def my_view(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.method == "POST":
        print("test csrf=====================================")
        print('Запрос: ' + str(request.POST))
        print('Куки: ' + str(request.COOKIES))
        dictPost = dict(request.POST)
        context = searchWorker(dictPost)

    elif request.method == "GET":

        category = request.GET.get("profession", "")

        context = searchWorker({'Profession': [category]})

    return render(request, 'SearchWorker.html', context)

def handle_uploaded_file(f, id):

    directory = 'C:/djangoprojects/main/static/main/media/'
    name      = 'foto/'+str(id)+'_'+'fff.png'

    #file = load(file)

    print(name)

    filename  = directory + name
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)

    return name