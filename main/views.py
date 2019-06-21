from django.http import  JsonResponse
from django.shortcuts import render
from expo.DataGet import  getProfessionList, getAllProfessionsAndGroups, getCityListFull, getServiceList, getCountryList, getCityList
from expo.DataSet import refreshLastOnline
from main.models import Professions, Service, UserType, News, Comments, Company, Attacment, CostOfService, Worker
import json
import logging

from django.middleware import csrf
# Create your views here.
logger = logging.getLogger(__name__)
logger1 = logging.getLogger('expo')



def show(request):

    logger.info('TEST LOGGING INFO')
    logger.debug('TEST LOGGING debug')
    logger.warning('TEST LOGGING warning')
    logger.error('TEST LOGGING error')
    logger.critical('TEST LOGGING critical')

    logger1.info('TEST LOGGING INFO')
    logger1.debug('TEST LOGGING debug')
    logger1.warning('TEST LOGGING warning')
    logger1.error('TEST LOGGING error')
    logger1.critical('TEST LOGGING critical')

    if request.user.is_authenticated:
        refreshLastOnline(request.user)



    print("Куки сновной страницы")
    print(print('coocies: ' + str(request.COOKIES)))

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

def showtest(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    context['all_workGroups']   = getAllProfessionsAndGroups()
    context['citylist']         = getCityListFull()

    #if request.user.is_authenticated:
    #    context['worker'] = getWorkerData(user_id = request.user, data = ['foto'])

    return render(request, 'index_ant.html', context)

def ServicesListSave(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated: # != True:

        if request.method == "POST":

            print(request.POST)

            if request.POST.__contains__('data'):

                #print(request.POST.__getitem__('data'))

                jsonString = json.loads(request.POST.__getitem__('data'))

                worker = UserType.GetElementByUser(request.user);

                if worker != None:
                    print ('aaaa')
                    print(jsonString)

                    CostOfService.objects.filter(idWorker=worker).delete()

                    for service in jsonString:
                        print ('ddddd')

                        price       = service.get('price')
                        idService   = service.get('id')

                        if price != '' and price != '0' and price != 0 and price != None:
                            try:
                                costofservice = CostOfService(idWorker=worker, idService = Service.objects.get(id=idService))
                                costofservice.price = float(price)
                                costofservice.save()
                            except:
                                print('ошибка при сохранении цены: '+str(worker)+'/'+str(idService))
                        else:
                            print('цена равна 0: '+str(worker)+'/'+str(idService))

            if request.is_ajax():

                return JsonResponse({'status': True, 'csrfmiddlewaretoken': csrf.get_token(request)})

            else:
                return HttpResponse(settings.HOME_PAGE + 'success/')

        else:
            if request.is_ajax():
                return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})
            else:
                return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)
    else:
        if request.is_ajax():
            return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})
        else:
            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def ProfessionsListSave(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated: # != True:

        if request.method == "POST":

            print(request.POST)

            if request.POST.__contains__('data'):

                jsonString = json.loads(request.POST.__getitem__('data'))

                worker = UserType.GetElementByUser(request.user);

                if worker != None:
                    print ('aaaa')
                    print(jsonString)

                    worker.professions.clear()

                    for prof in jsonString:

                        if prof.get('value') == True:
                            try:
                                worker.professions.add(Professions.objects.get(id=prof.get('id')))
                            except:
                                print("не удалось сохранить профессию")

            if request.is_ajax():
                return JsonResponse({'status': True, 'csrfmiddlewaretoken': csrf.get_token(request)})

            else:
                return HttpResponse(settings.HOME_PAGE + 'success/')

        else:
            if request.is_ajax():
                return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})
            else:
                return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)
    else:
        if request.is_ajax():
            return JsonResponse({'status': False, 'csrfmiddlewaretoken': csrf.get_token(request)})
        else:
            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

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
        {
            "title": 'Наличие визы',
            "type": 'boolean',
            "columnname": 'haveshengen',
        },

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

        elif userType == 2:
            data = {'name': elem.name, 'surname': '', 'fotourl': Attacment.getresizelink(elem.image) + str(elem.foto), 'id': str(elem.id)}

        else:
            data = {'name': '', 'surname': '', 'fotourl': '', 'id': ''}

        answer['status'] = True
        answer['user'] = data

    else:

        answer['status'] = False
        answer['errors'] = {'username': 'user is not authenticated'}

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

    resp = {'dataset': context, 'csrfmiddlewaretoken': csrf.get_token(request)}

    if not request.user.is_authenticated:
        resp['csrftoken'] = request.META["CSRF_COOKIE"]

    response = JsonResponse(resp)
    response['Access-Control-Allow-Origin'] = "*"

    return response
