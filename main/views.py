from django.http import  JsonResponse
from django.shortcuts import render, redirect
from expo.DataGet import  getFIOList, getProfessionList, getAllProfessionsAndGroups, getCityListFull, getServiceList, getCountryList, getCityList
from expo.DataSet import refreshLastOnline
from main.models import Professions, Service, UserType, News, Comments, Company, Attacment, CostOfService, Worker, ConfirmCodes
import json
import logging
from django.conf import settings

from django.middleware import csrf
# Create your views here.
logger = logging.getLogger(__name__)
logger1 = logging.getLogger('expo')

def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    all_profession = getProfessionList()
    all_Groups  = []
    profarray = []

    key = 1

    print(len(all_profession))

    for i in all_profession:

        profarray.append(i)
        if key % 7 == 0:
            all_Groups.append({'professions': profarray.copy()})
            profarray.clear()

        key = key + 1

    all_Groups.append({'professions': profarray.copy()})

    context['all_profession']   = all_Groups
    context['citylist']         = getCityListFull()
    context['comments']         = Comments.GetActual(Comments, position_begin=0, position_end=2)
    context['news']             = News.GetActual(News, position_begin=0, position_end=3)

    return render(request, 'index.html', context)

def sendlink(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.method == "POST":

        phone = request.POST.__getitem__("get_link_phone")
        type = request.POST.__getitem__("get_link_type")

        ConfirmCodes.SendLink(phoneNumber=phone, type=type)
        return redirect(settings.HOME_PAGE + 'success/', status=200)

    else:
        return redirect(settings.HOME_PAGE + 'forbiden/', status=403)

def showtest(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    context['all_workGroups']   = getAllProfessionsAndGroups()
    context['citylist']         = getCityListFull()

    #if request.user.is_authenticated:
    #    context['worker'] = getWorkerData(user_id = request.user, data = ['foto'])

    return render(request, 'index_ant.html', context)

def jsonProfessionList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getProfessionList()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonFioList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getFIOList(request.GET.get('order'))

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonServicesList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getServiceList()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonSelectionParameters(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    token = csrf.get_token(request);
    searchparams = [

        {
            "title": 'Профессия для поиска',
            "type": 'ref',
            "columnname": 'profession',
        },
        {
            "title": 'Город для поиска',
            "type": 'ref',
            "columnname": 'city',
        },

        {
            "title": 'Стаж работы',
            "type": 'list',
            "columnname": 'workexperience',
            "values": ['Не имеет значения', 'до 1 года', '1-3 года', '3-7 лет', 'более 7 лет']
        },


        {
            "title": 'Анкета проверена',
            "type": 'boolean',
            "columnname": 'datacheck',
        },

        {
            "title": 'ИП/Самозанятые',
            "type": 'boolean',
            "columnname": 'haveip',
        },
        #{
        #    "title": 'Наличие визы',
        #    "type": 'boolean',
        #    "columnname": 'haveshengen',
        #},

        {
            "title": 'Наличие загранпаспорта',
            "type": 'boolean',
            "columnname": 'haveintpass',
        },

        {
            "title": 'Проверен ФСО',
            "type": 'boolean',
            "columnname": 'fsocheck',
        },


        {
            "title": 'Свой инструмент',
            "type": 'boolean',
            "columnname": 'haveinstrument',
        },

        {
            "title": 'Только с отзывами',
            "type": 'boolean',
            "columnname": 'onlycomments',
        },


        {
            "title": 'Только с фото',
            "type": 'boolean',
            "columnname": 'onlyfoto',
        },

        {
            "title": 'Готов к командировкам',
            "type": 'boolean',
            "columnname": 'readytotravel',
        },

        {
            "title": 'Возраст',
            "type": 'range',
            "min": 18,
            "max": 70,
            "columnname": 'age',
        },

        {
            "title": 'Рейтинг',
            "type": 'rating',
            "columnname": 'inputrating',
        },

        {
            "title": 'Пол',
            "type": 'list',
            "columnname": 'sex',
            "values": ['Не имеет значения', 'Мужской', 'Женский']
        },


    ]

    resp = {'searchparams': searchparams, 'csrfmiddlewaretoken': token}

    if not request.user.is_authenticated:
        resp['csrftoken'] = request.META["CSRF_COOKIE"]

    response = JsonResponse(resp)

    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonCityList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getCityList()
    #context = getCityListFull()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonCityListGroup(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    #context = getCityList()
    context = getCityListFull()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonCountryList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    #context = getCityList()
    context = getCountryList()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def jsonCompanyList(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    companyList = []

    query = Company.objects.all().filter(block=False)

    for e in query:
        companyList.append({'name': e.name,
                'id': e.id,
                'url': '/company?id=' + str(e.id),
                'fotourl': Attacment.getlink(e.image),
                'resizefotourl': Attacment.getresizelink(e.image),
                'lastonline': e.lastOnline,
                'description': e.description
               })

    response = JsonResponse({'dataset': companyList})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def checkLogin(request):

    answer = {}

    print(request.COOKIES)

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)
        elem = UserType.GetElementByUser(request.user)

        if userType == 1:
            data = {'name': elem.name, 'surname': elem.surname, 'fotourl': Attacment.getresizelink(elem.image) + str(elem.foto), 'id': str(elem.id)}
            answer['usertype'] = 'worker'
        elif userType == 2:
            data = {'name': elem.name, 'surname': '', 'fotourl': Attacment.getresizelink(elem.image) + str(elem.foto), 'id': str(elem.id)}
            answer['usertype'] = 'company'
        else:
            data = {'name': '', 'surname': '', 'fotourl': '', 'id': ''}
            answer['usertype'] = ''
        answer['status'] = True
        answer['user'] = data

    else:

        answer['status'] = False
        answer['errors'] = {'username': 'user is not authenticated'}
        answer['usertype'] = ''

    response = JsonResponse(answer)
    response['Access-Control-Allow-Origin'] = "*"

    return response

def checkServer(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    response = JsonResponse({'status': True})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def showJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    print(request.GET)

    context = getAllProfessionsAndGroups()
    cookies = {'csrfmiddlewaretoken': csrf.get_token(request)}

    if not request.user.is_authenticated:
        cookies['csrftoken'] = request.META["CSRF_COOKIE"]

    resp = {'dataset': context, 'cookies': cookies}
    response = JsonResponse(resp)
    response['Access-Control-Allow-Origin'] = "*"

    return response
