from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from main.models import Comments, Worker, Professions, UserType, Company
from main.forms import CommentForm
from expo.DataGet import getComments, getProfessionListWithGroup, getServiceList, gerWorkList, searchWorker, getCityList, getCityListFull, getCountryList
from expo.DataSet import setWorker, refreshLastOnline
from django.views.decorators.csrf import csrf_exempt
from django.middleware import csrf
import json
from django.conf import settings


# Create your views here.
def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    return HttpResponse('Work Settings')

def saveSettings(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated: # != True:

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

                if request.is_ajax():

                    return JsonResponse({'status': True, 'csrfmiddlewaretoken': csrf.get_token(request)})

                else:
                    return HttpResponse(settings.HOME_PAGE + 'success/')

            elif userType == 2:

                if request.POST.__contains__('data'):

                    print("Сохраняем компанию")

                    print(request.POST.__getitem__('data'))

                    data = dict(json.loads(request.POST.__getitem__('data')))

                    Company.UpdateCompany(user=request.user, data=data)

                if request.is_ajax():

                    return JsonResponse({'status': True, 'csrfmiddlewaretoken': csrf.get_token(request)})

                else:

                    return HttpResponse(settings.HOME_PAGE + 'success/')

            else:

                if request.is_ajax():

                    return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})

                else:

                    return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

        else:

            if request.is_ajax():

                return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})

            else:

                return HttpResponse(settings.HOME_PAGE + 'notfound/', status=404)
    else:

        if request.is_ajax():

            return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})

        else:

            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

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
                       #'city': getCityList(),
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
            return render(request, 'errors/500.html', None, None, status=500)
    else:
        return render(request, 'errors/403.html', None, None, status=403)

def showSettingsJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.user.is_authenticated:

        print('Настройки: ' + str(request.POST))
        print('showSettingsJson куки:' + str(request.COOKIES))
        print('Настройки: ' + str(request.user))

        userType = UserType.GetUserType(request.user)

        if userType == 1:

            token = csrf.get_token(request)

            worker          = gerWorkList(user_id=request.user, userAauthorized=request.user.is_authenticated, itsSettings=True)
            selectedList    = []

            if worker != None and len(worker) > 0:
                worker          = worker[0]
                selectedList    = worker.get('proflist')
            else:
                worker          = {"name": "", "surname": "", "lastname":""}

            struct = {
                "group": [
                    {"name": "Фотография", "items": [
                        {"columnname": "fotourl", "type": "base64", "value": worker.get('resizefotourl', ''),
                            "additionaly":
                                {"rating": {"type": "int", "value": worker.get('rating', 0), 'hidden': True},
                                 "commentscount": {"type": "int", "value": worker.get('commentscount', 0), 'hidden': True}}
                        },
                    ]},
                    {"name": "Личные данные", "items": [
                        {"columnname": "surname", "label": "Фамилия", "type": "string", "value": worker.get('surname', ''), "required": True},
                        {"columnname": "name","label": "Имя", "type": "string", "value": worker.get('name', ''), "required": True},
                        {"columnname": "lastname", "label": "Отчество", "type": "string", "value": worker.get('lastname', '')},
                        {"columnname": "sex", "label": "Пол", "type": "binaryswitch", "values": ["Женский", "Мужской"],"value": 1 if (worker.get('sex', True)) else 0},
                        {"columnname": "birthday", "label": "Дата рождения", "type": "date", "value": worker.get('birthday', ''), "required": True},
                        {"columnname": "country", "label": "Гражданство", "type": "ref", "value": worker.get('nationality', '')},
                        {"columnname": "workpermit", "label": "Разрешение на работу в РФ", "type": "boolean", "value": worker.get('workpermit', False)},
                        {"columnname": "city", "label": "Мой город, населенный пункт", "type": "ref", "value": worker.get('city', '')},
                        {"columnname": "phonenumber", "label": "Телефон", "type": "string", "subtype": "phone", "value": worker.get('phonenumber', '')},
                        {"columnname": "emailaddress", "label": "Электронная почта", "type": "string", "subtype": "email", "value": worker.get('emailaddress', '')},
                        {"columnname": "haveip", "label": "ИП/Самозанятые", "type": "boolean", "value": worker.get('haveip', False)},
                        {"columnname": "haveinstrument", "label": "Есть свои инструменты", "type": "boolean", "value": worker.get('haveinstrument', False)},
                        {"columnname": "experiencedate", "label": "Работаю на выставках с", "type": "year", "min": 1990, "max": 2020, "value": worker.get('experiencedate', False)},
                        {"columnname": "experience", "label": "Опыт работы на выставках", "type": "text", "value": worker.get('experience', '')}
                    ]},
                    {"name": "Командировки", "items": [
                        {"columnname": "readytotravel", "label": "Готов к командировкам", "type": "boolean", "value": worker.get('readytotravel', False)},
                        {"columnname": "haveintpass", "label": "Наличие загранпаспорта", "type": "boolean", "value": worker.get('haveintpass', False)},
                        {"columnname": "haveshengen", "label": "Наличие визы", "type": "boolean", "value": worker.get('haveshengen', False)},
                    ]},
                    {"name": "Мои умения и навыки", "items": [
                        {"columnname": "professions", "label": "Специальность", "type": "multipleref", "value": worker.get('proflist', [])},
                    ]},
                    {"name": "Услуги и цены", "items": [
                        {"columnname": "salary", "label": "Должностной оклад (руб.)", "type": "int", "value": worker['works'].get('salary', 0)},
                        {"columnname": "services", "label": "Проектная работа", "type": "table", "value": worker['works'].get('servicelist', [])},
                    ]},
                    {"name": "Дополнительно", "items": [
                        #{"columnname": "personaldataisallowed", "label": "Согласен на обработку персональных данных", "labelposition": "right", "width": "100%", "type": "boolean", "value": worker.get('personaldataisallowed', False), "backgroundcolor": "#f8d7da"},
                        {"columnname": "publishdata", "label": "Опубликовать анкету в общий доступ", "labelposition": "right", "width": "100%", "type": "boolean", "value": worker.get('publishdata', False), "backgroundcolor": "#d4edda"},
                    ]}
                ]
            }

            context = {'worker': struct,
                            'itsworker': True,
                            'status': True,
                            'csrfmiddlewaretoken': token,
                            'userid': worker.get('id')}

        elif userType == 2:

            token = csrf.get_token(request)

            company = Company.GetCompanyByUser(user=request.user)

            worker = {"group": [
                        {"name": "Фотография", "items":
                            [{"columnname": "fotourl", "type": "base64", "value": company.get('resizefotourl', ''),},]
                         },
                        {"name": "Данные о компании", "items": [
                            {"columnname": "name", "label": "Наименование", "type": "string", "value": company.get('name', ''), "required": True},
                            {"columnname": "vatnumber", "label": "ИНН", "type": "string", "value": company.get('vatnumber', ''), "required": True},
                            {"columnname": "city", "label": "Мой город, населенный пункт", "type": "ref", "value": company.get('city', '')},
                            {"columnname": "phonenumber", "label": "Телефон", "type": "string", "subtype": "phone", "value": company.get('phonenumber', '')},
                            {"columnname": "emailaddress", "label": "Электронная почта", "type": "string", "subtype": "email", "value": company.get('emailaddress', '')},
                            {"columnname": "description", "label": "Описание", "type": "text", "value": company.get('description', '')}
                        ]
                         }
                        ]
                     }

            context = {'worker': worker,
                       'itsworker': False,
                       'status': True,
                       'csrfmiddlewaretoken': token,
                       'userid': company.get('id')}

        else:
            context["message"] = '500: Внутренняя ошибка сервера'
            context["status"] = False
    else:
        context["message"]  = '403: Доступ запрещен'
        context["status"]   = False

    return JsonResponse(context)

def showWorker(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    id = request.GET.get("id", None)

    if id == None:

        return render(request, 'errors/404.html', status=404)

    if request.method == "GET":

        commentForm = CommentForm()

    workerList  = gerWorkList(idWorker=[id], userAauthorized=userAauthorized, its_superuser=request.user.is_superuser)
    comments    = getComments(idWorker=id)

    print("Ответ:" + str(len(workerList)))
    if len(workerList) == 0:
        return render(request, 'errors/404.html', status=404)
    else:
        return render(request, 'Worker.html', {"worker": workerList[0], "commentForm": commentForm, "comments": comments, "userAauthorized": userAauthorized})

def showWorkersJson(request):

    #if request.user.is_authenticated:
    #    refreshLastOnline(request.user)

    #print(request.GET)

    #context = {"dataset": []}
    #context['Access-Control-Allow-Origin'] = "*"

    #return JsonResponse(context)

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    profession  = None
    id          = None

    print(request.GET)

    if request.method == "GET":

        profession = request.GET.get("profession", None)
        id = request.GET.get("id", None)

        if id != None:  #пока так
            id = [id]

    context = {}
    context["dataset"] = gerWorkList(idGroup=profession, idWorker=id, userAauthorized=request.user.is_authenticated, groupAttribute = True)


    context['Access-Control-Allow-Origin'] = "*"

    return JsonResponse(context)

def showSearchJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    print(request.POST)

    if request.method == "POST":

        print("test csrf=====================================")
        print('Запрос: ' + str(request.POST))
        print('Куки: ' + str(request.COOKIES))

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        print('шоу серч: '+ str(dictPost))
        context = searchWorker(user = request.user, searchList=dictPost, groupAttribute=True)

    elif request.method == "GET":

        category    = request.GET.get("profession", "")
        city        = request.GET.get("city", "")

        context = searchWorker(user = request.user,searchList={'profession': category, 'city': city}, userAauthorized=request.user.is_authenticated, groupAttribute=True)

    return JsonResponse(context)

def showSearch(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    print("Попали")

    if request.method == "POST":

        print("test csrf=====================================")
        print('Запрос: ' + str(request.POST))
        print('Куки: ' + str(request.COOKIES))

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(user = request.user, searchList=dictPost)

    elif request.method == "GET":

        category    = request.GET.get("profession", '')
        city        = request.GET.get("city", '')

        context = searchWorker(user = request.user, searchList={'profession': category, 'city': city}, userAauthorized=request.user.is_authenticated)

    context["count"] = len(context.get('dataset'))

    print("Количество: "+ str(context["count"]))

    context['citylist'] = getCityListFull()
    context['servicelist'] = getServiceList()

    return render(request, 'SearchWorker.html', context)

def showWorkersList(request):

    context = {}

    if request.method == "POST":

        print("test csrf=====================================")
        print('Запрос: ' + str(request.POST))
        print('Куки: ' + str(request.COOKIES))

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(user = request.user, searchList=dictPost)

        context["count"] = len(context.get('dataset'))

    return render(request, 'includes/WorkerList.html', context);

def showSearchTest(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {"count": 0}

    if request.method == "POST":

        dictPost = dict(json.loads(request.POST.__getitem__('data')))
        context = searchWorker(user = request.user, searchList=dictPost, userAauthorized = request.user.is_authenticated, returnCount = True)

    return JsonResponse(context)

def showCommentsJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {"dataset":[]}

    if request.method == "GET":
        userid = request.GET.get("userid", "")

        if userid != "":
            context["dataset"] = getComments(idWorker=userid)

    context['csrfmiddlewaretoken'] = csrf.get_token(request)

    return JsonResponse(context)

def saveComments(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:# != True:
        if request.method == "POST":

            if request.POST.__contains__('data'):

                data = dict(json.loads(request.POST.__getitem__('data')))

                Comment = Comments()

                Comment.idUser   = request.user
                Comment.idWorker = get_object_or_404(Worker, id=data.get("idworker"))
                Comment.text     = data.get("text")
                Comment.rating   = data.get("rating")
                Comment.idProf   = get_object_or_404(Professions, id=data.get("idprofession"))
                Comment.save()

                return HttpResponse(settings.HOME_PAGE + 'success/')

            return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

        else:
            return render(request, 'errors/404.html', None, None, status=404)
    else:
        return render(request, 'errors/403.html', None, None, status=403)

@csrf_exempt
def my_view(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.method == "POST":
        print("test csrf=====================================")
        print('Запрос: ' + str(request.POST))
        print('Куки: ' + str(request.COOKIES))

        #jsonString = json.loads(request.POST.__getitem__('data'))

        print("test body=====================================")
        #print(jsonString);


        #dictPost = dict(json.loads(request.POST.__getitem__('data')))
        #context = searchWorker(user = request.user, searchList=dictPost)

        #context["count"] = len(context.get('dataset'))

    elif request.method == "GET":

        category = request.GET.get("profession", "")

        context = searchWorker({'Profession': category})

    return JsonResponse(context)
