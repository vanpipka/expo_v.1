from django.http import HttpResponse , JsonResponse
from django.shortcuts import render, redirect
from expo.DataGet import getProfessionListWithGroup, getProfessionList, getAllProfessionsAndGroups, getCityListFull, getCityList, getServiceList
from expo.DataSet import refreshLastOnline
from django.middleware import csrf
# Create your views here.

def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)
    print("Куки сновной страницы")
    print(print('coocies: ' + str(request.COOKIES)))

    context = {}

    context['all_workGroups']   = getAllProfessionsAndGroups()

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

    context['all_profession'] = all_Groups

    context['citylist']         = getCityListFull()

    #if request.user.is_authenticated:
    #    context['worker'] = getWorkerData(user_id = request.user, data = ['foto'])

    return render(request, 'index.html', context)

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
            "title": 'Профессия',
            "type": 'ref',
            "columnname": 'profession',
        },
        {
            "title": 'Город',
            "type": 'ref',
            "columnname": 'city',
        },
        {
            "title": 'Пол',
            "type": 'list',
            "columnname": 'sex',
            "values": ['Не имеет значения', 'Мужской', 'Женский']
        },
        {
            "title": 'Свой инструмент',
            "type": 'boolean',
            "columnname": 'haveinstrument',
        },
        {
            "title": 'Есть ИП',
            "type": 'boolean',
            "columnname": 'haveip',
        },
        {
            "title": 'Шенгенская виза',
            "type": 'boolean',
            "columnname": 'haveshengen',
        },

        {
            "title": 'Есть загранпаспорт',
            "type": 'boolean',
            "columnname": 'haveintpass',
        },

        {
            "title": 'Проверен ФСО',
            "type": 'boolean',
            "columnname": 'fsocheck',
        },

        {
            "title": 'Только с отзывами',
            "type": 'boolean',
            "columnname": 'onlycomments',
        },


        {
            "title": 'Данные проверены',
            "type": 'boolean',
            "columnname": 'datacheck',
        },

        {
            "title": 'Рейтинг',
            "type": 'rating',
            "columnname": 'inputrating',
        },

        {
            "title": 'Стаж работы',
            "type": 'list',
            "columnname": 'experience',
            "values": ['Не имеет значения', 'до 1 года', '1-3 года', '3-7 лет', 'более 7 лет']
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

    #context = getCityList()
    context = getCityListFull()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response

def showJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = getAllProfessionsAndGroups()

    response = JsonResponse({'dataset': context})
    response['Access-Control-Allow-Origin'] = "*"

    return response


