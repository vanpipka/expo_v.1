from datetime import *
from django.utils import timezone
from main.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from datetime import date, timedelta

def getStatistics(user):
    content     = {}

    #Получаем данные по регистрациям за последние 10 дней
    newusers    = []
    sdate       = timezone.now()

    print(sdate)
    i           = 10
    while i >= 0:
        ndate = sdate - timedelta(days=i)
        newusers.append({"date":  str(ndate.day)+"."+str(ndate.month), "count": User.objects.filter(date_joined__range=(ndate, ndate + timedelta(days=1))).count()})
        i = i-1


    content["newUsers"] = newusers

    #Получаем данные по посещениям за последние 10 дней
    visits= []
    sdate       = timezone.now()

    print(sdate)
    i           = 10
    while i >= 0:
        ndate = sdate - timedelta(days=i)
        visits.append({"date":  str(ndate.day)+"."+str(ndate.month), "count": UserActivity.objects.filter(date__range=(ndate, ndate + timedelta(days=1))).count()})
        i = i-1

    content["visits"] = visits

    #Получаем общее количество ползователей по профессиям
    professions    = []
    for p in Professions.objects.all().order_by("-workerСount"):
        professions.append({
                    "name": p.name,
                    "count": p.workerСount
                });

    professions.append({
                "name": "Без профессии",
                "count": Worker.objects.filter(professions__isnull=True).count()
            });

    content["professions"] = professions

    return content

def getAllProfessionsAndGroups(count = None):

    all_workGroups = []

    for e in WorkGroup.objects.all():

        all_professions = []
        AllProfessions  = Professions.objects.all().filter(idWorkGroup=e.id)

        if (count != None):
            AllProfessions = AllProfessions[:count]

        for p in AllProfessions:

            all_professions.append({"id": p.id,
                                    "name": p.name,
                                    "url_json": '/worker/m/info?profession='+str(p.id),
                                    "url": '/worker/search?profession='+p.name,
                                    "workercount": p.workerСount})

        all_workGroups.append({"name": e.name, "id": e.id, "items": all_professions})

    #context = all_workGroups
    #context = {"dataset": all_workGroups}
    #           "all_professions": all_professions}

    return all_workGroups

def getFIOList(order):

    print("fio: " + str(order))
    array = []

    if order == None:
        data = Worker.objects.all().values('name', 'surname')
    else:
        data = Worker.objects.all().filter(Q(name__iexact=order) | Q(surname__iexact=order)).values('name', 'surname')

    context = []
    for p in data:

        index = p['name'] + p['surname']

        if (index in array) != True:
            array.append(index)

            context.append({
                        "name": p['surname'] +" "+ p['name']
                    });

    return context

def getProfessionList():

    context = []
    for p in Professions.objects.all().order_by("-workerСount"):
        context.append({
                    "id": p.id,
                    "name": p.name,
                    "workercount": p.workerСount,
                    "url_json": '/worker/m/info?profession=' + str(p.id),
                    "url": '/worker/search?profession=' + p.name
                });

    return context

def getProfessionListWithGroup(count = None, selectedList=[]):

    context = {}
    for e in WorkGroup.objects.all():

        prof = []
        for p in Professions.objects.all().filter(idWorkGroup=e.id):
            selected = False

            for s in selectedList:
                if p.id == s['id']:
                    selected = True

            prof.append({"id": p.id, "name": p.name, "selected": selected})

        context[e.name] = prof

    return context

def gerWorkList(user=None, idGroup=None, count=None, idWorker=None, userAauthorized=False, user_id = None, itsSettings = False, groupAttribute = False, its_superuser=False):

    print("gerWorkList: "+str(user))
    if user == None or user.is_authenticated !=True:
        print("gerWorkList1 ")
        userType = None
    else:
        print("gerWorkList2 ")
        userType = UserType.GetUserType(user)
    print("userType: "+str(userType))
    nowDate  = timezone.now()
    WorkList = []

    if user_id != None:
        print("1")
        querySet = Worker.getWorkerQueryByUser(user=user_id)

    elif idWorker != None:
        print("2")
        querySet = Worker.objects.all().filter(id__in=idWorker)

    else:
        print("3")
        querySet = Worker.objects.all()

        if idGroup != None:
            print("3.1")
            querySet = querySet.filter(professions__id = idGroup)

        if count != None:
            print("3.2")
            querySet = querySet[:count]

    if itsSettings != True and its_superuser !=True:
        print("4")
        querySet = querySet.filter(publishdata=True)

    if its_superuser != True and itsSettings != True:
        print("5")
        querySet = querySet.filter(block=False)

    querySet = querySet.select_related('idCity').select_related('nationality')

    for e in querySet:

        print(str(e.name) + str(e.surname))

        media_url = settings.MEDIA_URL

        ratingInfo = Worker.getWorkerRating(e)

        WorkerInfo = {"id": e.id,
                        "description": e.Description,
                        "name": e.name,
                        "surname": e.surname,
                        "lastname": e.lastname,
                        "fullname": e.name + " "+e.surname,
                        "lastname": e.lastname,
                        "experiencedate": nowDate.year if e.Experiencewith == None else e.Experiencewith.year,
                        "experienceyear": 0 if e.Experiencewith == None else calculate_age(e.Experiencewith),
                        "rating": ratingInfo["rating"],
                        "commentscount": ratingInfo["commentsCount"],
                        "lastonline": e.lastOnline,
                        "url_json": '/worker/m/info?id='+str(e.id),
                        "url": '/worker/info?id='+str(e.id),
                        "education": e.education,
                        "publishdata": e.publishdata,
                        "birthday": e.birthday,
                        "age": calculate_age(e.birthday),
                        "experience": e.experience,
                        "sex": e.sex,
                        "personaldataisallowed": e.personaldataisallowed,
                        "cityname": e.idCity.name,
                        "city": {"id": e.idCity.id, "name": e.idCity.name},
                        "nationality": {"id": e.nationality.id, "name": e.nationality.name},
                        "isonline": True if (nowDate-e.lastOnline).seconds/60 < 5 else False}
        #print(str((nowDate-e.lastOnline).seconds/60< 5))
        #print("Количество секунд:" + str(nowDate) + " - " +str(e.lastOnline) +" = "+ str((nowDate - e.lastOnline).seconds))
        #print("Пользователь онлайн: "+str(WorkerInfo['isonline']))

        #if e.idCity:
        #    WorkerInfo["city"] = e.idCity.name
        #else:
        #    WorkerInfo["city"] = ""

        if its_superuser:
            WorkerInfo["block"] = e.block

        if groupAttribute:

            attributeArray = []
            attributeArray.append({"name": "haveip", "label": "ИП/Самозанятый", "value": e.haveIP})
            attributeArray.append({"name": "fsocheck", "label": "Проверка ФСО", "value": e.fsocheck})
            attributeArray.append({"name": "haveinstrument", "label": "Есть инструмент", "value": e.haveInstrument})
            attributeArray.append({"name": "workpermit", "label": "Разрешение на работу РФ", "value": e.workpermit})
            attributeArray.append({"name": "datacheck", "label": "Анкета проверена", "value": e.datacheck})
            #attributeArray.append({"name": "haveshengen", "label": "Наличие визы", "value": e.haveShengen})
            attributeArray.append({"name": "haveintpass", "label": "Наличие загранпаспорта", "value": e.haveIntPass})
            attributeArray.append({"name": "readytotravel", "label": "Готов к командировкам", "value": e.readytotravel})

            WorkerInfo["attributes"] = attributeArray

        else:
            WorkerInfo["haveip"] = e.haveIP
            WorkerInfo["fsocheck"] = e.fsocheck
            WorkerInfo["haveinstrument"] = e.haveInstrument
            WorkerInfo["workpermit"] = e.workpermit
            WorkerInfo["datacheck"] = e.datacheck
            #WorkerInfo["haveshengen"] = e.haveShengen
            WorkerInfo["haveintpass"] = e.haveIntPass
            WorkerInfo["readytotravel"] = e.readytotravel

        #if e.foto:
        WorkerInfo["fotourl"] = Attacment.getlink(e.image)
        WorkerInfo["resizefotourl"] = Attacment.getresizelink(e.image)
        #else:
        #WorkerInfo["fotourl"] = '/static/main/img/add-photo.png'
        #WorkerInfo["resizefotourl"] = '/static/main/img/add-photo.png'

        if e.Experiencewith != None:
            WorkerInfo["experiencewith"] = calculate_age(e.Experiencewith) # Переделать на разность дат
        else:
            WorkerInfo["experiencewith"] = 0

        print("Перед первой проверкой")

        if userType == 2 or itsSettings:
            WorkerInfo["phonenumber"] = e.phonenumber
            WorkerInfo["emailaddress"] = e.emailaddress
        else:
            WorkerInfo["phonenumber"] = ""
            WorkerInfo["emailaddress"] = ""

        workerid    = e.id
        profList    = []
        priceList   = []
        attachments = []

        #Профессии
        for prof in e.professions.all():
            profList.append({"id": prof.id, "name": prof.name})

        WorkerInfo["proflist"] = profList

        #for attachment in e.WorkerAttachment.all():
        #    attachments.append({"id": attachment.id, "url": '/static/main/media/' + str(attachment.file), "resizeurl": '/static/main/media/resize' + str(attachment.file),  "description": attachment.Description})
        WorkerInfo["attachments"] = attachments

        #Цены на услуги
        works = {}
        if userType == 2 or itsSettings:
            for prof in CostOfService.objects.all().filter(idWorker=workerid).select_related('idService'):
                priceList.append({"id": prof.idService.id, "service": prof.idService.name, "price": prof.price, "unit": prof.idService.unit})

            works = {'salary': e.salary, 'servicelist': priceList}

        WorkerInfo['works'] = works

        WorkerInfo["servicelist"] = priceList

        WorkList.append(WorkerInfo)

    return WorkList

def getMinWorkerList():

    workerlist = []
    querySet = Worker.objects.filter(publishdata=True)

    for e in querySet:
        workerlist.append({"id": e.id, "name": e.name, "resizefotourl": Attacment.getresizelink(e.image)})

    return workerlist

def getComments(idWorker):

    commentsList = []
    query = Comments.objects.filter(idWorker=idWorker).filter(moderation=True).order_by("-created").select_related('idWorker').select_related('idProf')

    for e in query:

        user = UserType.GetElementByUser(e.idUser)

        if user != None:

            commentsList.append({
                "user": {"id": user.id, "name": user.name, "fotourl": Attacment.getresizelink(user.image)},
                "worker": {"id": e.idWorker.id, "name": e.idWorker.name, "fotourl": Attacment.getresizelink(e.idWorker.image)},
                "profession": {"id": e.idProf.id, "name": e.idProf.name},
                "text": e.text,
                "created": e.created,
                "moderation": e.moderation,
                "rating": e.rating,
            })

    return commentsList

def getWorker(id):

    try:
        worker = Worker.objects.get(id=id)
    except ObjectDoesNotExist:
        worker = Worker(id=id)

    return worker

def getCityList():

  cityList = []
  querySet = City.objects.all().filter()

  for e in querySet:

      cityList.append({'id': e.id, 'name': e.name})

  return cityList

def getServiceList():

    cityList = []
    querySet = Service.objects.all().filter()

    for e in querySet:
        cityList.append({'id': e.id, 'name': e.name})

    return cityList

def getCountryList():

    countryList = []
    querySet = Country.objects.all().filter()

    for e in querySet:
        countryList.append({'id': e.id, 'name': e.name})

    return countryList

def getCityListFull():

    cityList = []
    fullList = []
    cityQuerySet    = City.objects.all().filter().select_related('region').select_related('country')
    regionQuerySet  = Region.objects.all().filter()

    for e in cityQuerySet:
        cityList.append({'id': e.id, 'name': e.name, 'region': e.region.id, 'country': e.country.name})

    for e in regionQuerySet:

        m = []

        for city in cityList:

            if city['region'] == e.id:

                city['region'] == e.name

                m.append(city)

        fullList.append({'name': e.name, 'id': e.id, 'items': m})

    return fullList

def searchWorker(user, searchList, userAauthorized=False, returnCount = False, groupAttribute=False):

    print(searchList)

    context         = {}
    searchProperty  = {'WorkExperience': 'WorkExperience0'}
    profession      = searchList.get('profession')
    city            = searchList.get('city')
    workexperience  = str(searchList.get('workexperience'))
    onlyfoto        = searchList.get('onlyfoto')
    onlycomments    = searchList.get('onlycomments')
    rating          = searchList.get('inputrating')
    fsocheck        = searchList.get('fsocheck')
    datacheck       = searchList.get('datacheck')
    sex             = str(searchList.get('sex'))
    haveip          = searchList.get('haveip')
    haveshengen     = searchList.get('haveshengen')
    haveintpass     = searchList.get('haveintpass')
    haveinstrument  = searchList.get('haveinstrument')
    positionfrom    = searchList.get('positionfrom')
    positionto      = searchList.get('positionto')
    workpermit      = searchList.get('workpermit')
    age             = searchList.get('age')
    readytotravel   = searchList.get('readytotravel')
    price           = searchList.get('salary')
    projectwork     = searchList.get('projectwork')

    if positionfrom == None:
        positionfrom = 0
    else:
        positionfrom = int(positionfrom)

    if positionto == None:
        positionto = positionfrom + 5

    searchquery     = Worker.objects.all()

    # Отбор по таблице рейтинг отдельно, пока не умею делать левое соединение

    isOnlyComments  = onlycomments != None and onlycomments == True
    isRating        = rating != None and rating != '' and rating != 0

    if isOnlyComments or isRating:
        ratingList  = []
        queryRating = None

        if isOnlyComments:

            print("Только с комментариями: Истина")
            searchProperty["onlycomments"] = True
            queryRating = Comments.objects.all().filter(moderation=True).values('idWorker').distinct()

        if isRating:
            print("Рейтинг более: "+str(rating))
            searchProperty["inputrating"] = rating
            if queryRating == None:
                queryRating = WorkerRating.objects.all()

            queryRating = queryRating.filter(rating__gte=rating).values('idWorker').distinct()

        for elem in queryRating:
            print('----------------------')
            ratingList.append(elem.get('idWorker'))

        searchquery = searchquery.filter(id__in = ratingList)

    if projectwork != None and projectwork != '':

        projectsearchList = []
        projectsearch = CostOfService.objects.all()

        for i in projectwork:

            print('j: '+str(i))
            projectsearch = projectsearch.filter(price__lte=int(i.get('price'))).filter(idService=i.get('id')).values('idWorker').distinct()

            for elem in projectsearch:
                id = elem.get('idWorker')

                try:
                    k = projectsearchList.index(id)
                except ValueError:
                    k = None

                if k == None:
                    projectsearchList.append(elem.get('idWorker'))

        searchquery = searchquery.filter(id__in=projectsearchList)

    if fsocheck != None and fsocheck == True:
        print("Проверка ФСО:" + str(fsocheck))
        searchProperty["fsocheck"] = True
        searchquery     = searchquery.filter(fsocheck=True)

    if readytotravel != None and readytotravel == True:
        print("Готов к командировкам:" + str(readytotravel))
        searchProperty["readytotravel"] = True
        searchquery = searchquery.filter(readytotravel=True)

    if workpermit != None and workpermit == True:
        print("Есть разрешение на работу:" + str(workpermit))
        searchProperty["workpermit"] = True
        searchquery     = searchquery.filter(workpermit=True)

    if haveshengen != None and haveshengen == True:
        print("Есть шенген:" + str(haveshengen))
        searchProperty["haveshengen"] = True
        searchquery     = searchquery.filter(haveShengen=True)

    if haveinstrument != None and haveinstrument == True:
        print("Есть инструмент:" + str(haveinstrument))
        searchProperty["haveinstrument"] = True
        searchquery     = searchquery.filter(haveInstrument=True)

    if haveintpass != None and haveintpass == True:
        print("Есть загранпаспорт:" + str(haveintpass))
        searchProperty["haveintpass"] = True
        searchquery     = searchquery.filter(haveIntPass=True)

    if haveip != None and haveip == True:
        print("Есть ИП:" + str(haveip))
        searchProperty["haveip"] = True
        searchquery     = searchquery.filter(haveIP=True)

    if sex != None and sex != '':
        print("Пол:" + str(sex))
        searchProperty["sex"] = sex

        if sex == 'M' or sex == '1':
            searchquery     = searchquery.filter(sex=True)
        elif sex == 'W' or sex == '2' :
            searchquery     = searchquery.filter(sex=False)
    else:
        searchProperty["sex"] = ''

    if datacheck != None and datacheck == True:
        print("Данные проверены:" + str(datacheck))
        searchProperty["datacheck"] = True
        searchquery     = searchquery.filter(datacheck=True)

    if profession != None and profession != '':
        print("Профессия:" + str(profession))
        searchProperty["profession"] = profession
        searchquery     = searchquery.filter(professions__indexName__contains=profession.upper())

    if price != None and price != '':
        print("Цена:" + str(price))
        searchProperty["salary"] = price

        if price == '1':
            searchquery = searchquery.filter(salary__lte=50000)
        elif price == '2':
            searchquery = searchquery.filter(salary__gte=50000).filter(salary__lte=100000)
        elif price == '3':
            searchquery = searchquery.filter(salary__gte=100000).filter(salary__lte=150000)
        elif price == '4':
            searchquery = searchquery.filter(salary__gte=150000)

    if city != None and city != '':
        print("Город:" + str(city))
        searchProperty["city"] = city
        searchquery = searchquery.filter(idCity__indexName__contains=city.upper())

    if workexperience != None  and workexperience != '0':

        workexperience = workexperience
        searchProperty["workexperience"] = "workexperience"+str(workexperience)
        if workexperience == '1':
            searchquery = searchquery.filter(Experiencewith__year__gte = timezone.now().year)
        elif workexperience == '2':
            searchquery = searchquery.filter(Experiencewith__year__gte = timezone.now().year-3).exclude(Experiencewith__year__gte = timezone.now().year)
        elif workexperience == '3':
            searchquery = searchquery.filter(Experiencewith__year__gte = timezone.now().year-7).exclude(Experiencewith__year__gte = timezone.now().year-3)
        elif workexperience == '4':
            searchquery = searchquery.exclude(Experiencewith__year__gte = timezone.now().year-7)

        print("Опыт работы:" + str(workexperience))

    if age != None and age != '':

        age_from    = age.get('min', '')
        age_to      = age.get('max', '')

        if age_from != None and age_from != '' and age_from != 18:

            print('Возраст от: '+str(age_from))

            datefrom = datetime.date(timezone.now().year - int(age_from), timezone.now().month, timezone.now().day)

            searchquery = searchquery.exclude(birthday__gte=datefrom)

        if age_to != None and age_to != '' and age_to != 70:

            print('Возраст до: '+str(age_to))

            datefrom = datetime.date(timezone.now().year - int(age_to) - 1, timezone.now().month, timezone.now().day)

            searchquery = searchquery.filter(birthday__gte=datefrom)

    if onlyfoto != None and onlyfoto == True:
        print("Только с фото: Истина")
        searchProperty["onlyfoto"] = True
        searchquery = searchquery.exclude(image__id='00000000000000000000000000000000')

    if searchquery != None:

        searchquery = searchquery.filter(publishdata=True)

        searchquery = searchquery.filter(block=False)

        if positionfrom != None and positionto!=None and returnCount!=True:
            searchquery = searchquery[positionfrom:positionto]

        if returnCount:

            context["count"] = len(searchquery)

        else:
            workerid = []

            for elem in searchquery:
                workerid.append(elem.id)

            print("before gerWorkList")
            workerList = gerWorkList(user = user, idWorker=workerid, userAauthorized=userAauthorized, groupAttribute=groupAttribute, its_superuser=user.is_superuser)

            context["dataset"] = workerList
            context["searchproperty"] = searchProperty

    context["nextposition"] = positionto

    return context

def getServiceList(searchLine = None):

    serviceList = []
    querySet = Service.objects.all()

    if searchLine != None:
        querySet = querySet.filter(name__contains=searchLine)

    for e in querySet:
        serviceList.append({'id': e.id, 'name': e.name})

    return serviceList

def calculate_age(born):

    try:
        today = datetime.datetime.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except:
        age = 0

    return 0 if age > 65 else age
