from datetime import *
from main.models import *

def getAllProfessionsAndGroups(count = None):

    all_workGroups = []

    for e in WorkGroup.objects.all():

        all_professions = []
        AllProfessions = Professions.objects.all().filter(idWorkGroup=e.id)

        if (count != None):
            AllProfessions = AllProfessions[:count]

        for p in AllProfessions:

            all_professions.append({"id": p.id,
                                    "name": p.name,
                                    "url_json": '/worker/m/info?profession='+str(p.id),
                                    "url": '/worker/search?profession='+p.name})

        all_workGroups.append({"name": e.name, "id": e.id, "professions": all_professions})

    #context = all_workGroups
    context = {"all_workGroups": all_workGroups}
    #           "all_professions": all_professions}

    return context

def getProfessionList():

    context = []
    for p in Professions.objects.all():
        context.append({"id": p.id, "name": p.name})

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

def gerWorkList(idGroup=None, count=None, idWorker=None, userAauthorized=False, user_id = None):

    nowDate  = datetime.datetime.now(timezone.utc)
    WorkList = []
    querySet = None

    if idGroup == None:
        querySet = Worker.objects.all()

    else:
        querySet = Worker.objects.all().filter(professions__id = idGroup)

    if count != None:
        querySet = querySet[:count]

    if idWorker != None:
        querySet = querySet.filter(id__in=idWorker)

    if user_id != None:
        querySet = querySet.filter(user_id=user_id)

    for e in querySet:

        ratingInfo = getWorkerRating(e)

        WorkerInfo = {"id": e.id,
                        "description": e.Description,
                        "name": e.name,
                        "surname": e.surname,
                        "lastname": e.lastname,
                        "haveip": e.haveIP,
                        "fsocheck": e.fsocheck,
                        "workpermit": e.workpermit,
                        "datacheck": e.datacheck,
                        "city": e.idCity.name,
                        "experiencewith": datetime.datetime.now().year - e.Experiencewith.year, # Переделать на разность дат
                        "experiencedate": e.Experiencewith,
                        "rating": ratingInfo["rating"],
                        "commentscount": ratingInfo["commentsCount"],
                        "lastonline": e.lastOnline,
                        "url_json": '/worker/m/info?id='+str(e.id),
                        "url": '/worker/info?id='+str(e.id),
                        "fotourl": '/static/main/media/' + str(e.foto),
                        "education": e.education,
                        "experience": e.experience,
                        "isonline": True if (nowDate-e.lastOnline).seconds/60 < 5 else False}
        #print(str((nowDate-e.lastOnline).seconds/60< 5))
        #print("Количество секунд:" + str(nowDate) + " - " +str(e.lastOnline) +" = "+ str((nowDate - e.lastOnline).seconds))
        #print("Пользователь онлайн: "+str(WorkerInfo['isonline']))

        if userAauthorized:
            WorkerInfo["phonenumber"] = e.phonenumber
            WorkerInfo["emailaddress"] = e.emailaddress
        else:
            WorkerInfo["phonenumber"] = ""
            WorkerInfo["emailaddress"] = ""

        workerid    = e.id
        profList    = []
        priceList   = []

        #Профессии
        for prof in e.professions.all():
            profList.append({"id": prof.id, "name": prof.name})
        WorkerInfo["proflist"] = profList

        #Цены на услуги
        for prof in CostOfService.objects.all().filter(idWorker=workerid).select_related('idService'):
            priceList.append({"service": prof.idService.name, "price": prof.price})
        WorkerInfo["servicelist"] = priceList

        #Добавим информацию о сотруднике в список
        WorkList.append(WorkerInfo)

    return WorkList

def getWorker(id):

    try:
        worker = Worker.objects.get(id=id)
    except:
        worker = Worker(id=id)

    return worker

def getWorkerRating(worker):

    ratingList = {"rating":0, "commentsCount":0}

    try:
        workerRating = WorkerRating.objects.get(idWorker=worker)
        ratingList["rating"] = workerRating.rating
        ratingList["commentsCount"] = workerRating.commentsCount

    except:
        print("рейтинг для "+ str(worker) +" не найден")

    return ratingList

def getCityList():

  cityList = []
  querySet = City.objects.all().filter()

  for e in querySet:

      cityList.append({'id': e.id, 'name': e.name})

  return cityList

def searchWorker(searchList, userAauthorized=False):

    print(searchList)

    context         = {}
    searchProperty  = {'WorkExperience': 'WorkExperience0'}
    profession      = searchList.get('Profession')
    city            = searchList.get('City')
    workExperience  = searchList.get('WorkExperience')
    onlyFoto        = searchList.get('OnlyFoto')
    onlyComments    = searchList.get('OnlyComments')
    rating          = searchList.get('InputRating')
    fsocheck        = searchList.get('FsoCheck')
    dataCheck       = searchList.get('DataCheck')
    sex             = searchList.get('Sex')
    haveIp          = searchList.get('HaveIp')
    haveShengen     = searchList.get('HaveShengen')
    haveIntPass     = searchList.get('HaveIntPass')
    haveInstrument  = searchList.get('HaveInstrument')
    searchquery     = Worker.objects.all()

    # Отбор по таблице рейтинг отдельно, пока не умею делать левое соединение

    isOnlyComments  = onlyComments != None and len(onlyComments) > 0 and onlyComments[0] == 'True'
    isRating        = rating != None and len(rating) > 0 and rating[0] != ''

    if isOnlyComments or isRating:
        ratingList  = []
        queryRating = None

        if isOnlyComments:

            print("Только с комментариями: Истина")
            searchProperty["OnlyComments"] = True
            queryRating = WorkerRating.objects.all()

        if isRating:
            print("Рейтинг более: "+str(rating[0]))
            searchProperty["InputRating"] = rating[0]
            if queryRating == None:
                queryRating = WorkerRating.objects.all()

            queryRating = queryRating.filter(rating__gte=rating[0])

        for elem in queryRating:
            print('----------------------')
            ratingList.append(elem.idWorker_id)

        searchquery = searchquery.filter(id__in = ratingList)

    if fsocheck != None and len(fsocheck) > 0 and fsocheck[0] == 'True':
        print("Проверка ФСО:" + str(fsocheck[0]))
        searchProperty["FsoCheck"] = True
        searchquery     = searchquery.filter(fsocheck=True)

    if haveShengen != None and len(haveShengen) > 0 and haveShengen[0] == 'True':
        print("Есть шенген:" + str(haveShengen[0]))
        searchProperty["HaveShengen"] = True
        searchquery     = searchquery.filter(haveShengen=True)

    if haveInstrument != None and len(haveInstrument) > 0 and haveInstrument[0] == 'True':
        print("Есть инструмент:" + str(haveInstrument[0]))
        searchProperty["HaveInstrument"] = True
        searchquery     = searchquery.filter(haveInstrument=True)

    if haveIntPass != None and len(haveIntPass) > 0 and haveIntPass[0] == 'True':
        print("Есть загранпаспорт:" + str(haveIntPass[0]))
        searchProperty["HaveIntPass"] = True
        searchquery     = searchquery.filter(haveIntPass=True)

    if haveIp != None and len(haveIp) > 0 and haveIp[0] == 'True':
        print("Есть ИП:" + str(haveIp[0]))
        searchProperty["HaveIp"] = True
        searchquery     = searchquery.filter(haveIP=True)

    if sex != None and len(sex) > 0 and sex[0] != '':
        print("Пол:" + str(sex[0]))
        searchProperty["Sex"] = sex[0]

        if sex[0] == 'M':
            searchquery     = searchquery.filter(sex=True)
        elif sex[0] == 'W':
            searchquery     = searchquery.filter(sex=False)

    if dataCheck != None and len(dataCheck) > 0 and dataCheck[0] == 'True':
        print("Данные проверены:" + str(dataCheck[0]))
        searchProperty["DataCheck"] = True
        searchquery     = searchquery.filter(datacheck=True)

    if profession != None and len(profession) > 0 and profession[0] != '':
        print("Профессия:" + str(profession[0]))
        searchProperty["Profession"] = profession[0]
        searchquery     = searchquery.filter(professions__indexName__contains=profession[0].upper())

    if city != None and len(city) > 0 and city[0] != '':
        print("Город:" + str(city[0]))
        searchProperty["City"] = city[0]
        searchquery = searchquery.filter(idCity__indexName__contains=city[0].upper())

    if workExperience != None and len(workExperience) > 0 and workExperience[0] != '':

        workExperience = workExperience[0]
        searchProperty["WorkExperience"] = "WorkExperience"+str(workExperience)
        if workExperience == '1':
            searchquery = searchquery.filter(Experiencewith__year__gte = datetime.datetime.now().year)
        elif workExperience == '2':
            searchquery = searchquery.filter(Experiencewith__year__gte = datetime.datetime.now().year-3).exclude(Experiencewith__year__gte = datetime.datetime.now().year)
        elif workExperience == '3':
            searchquery = searchquery.filter(Experiencewith__year__gte = datetime.datetime.now().year-7).exclude(Experiencewith__year__gte = datetime.datetime.now().year-3)
        elif workExperience == '4':
            searchquery = searchquery.exclude(Experiencewith__year__gte = datetime.datetime.now().year-7)

        print("Опыт работы:" + str(workExperience))

    if onlyFoto != None and len(onlyFoto) > 0 and onlyFoto[0] == 'True':
        print("Только с фото: Истина")
        searchProperty["OnlyFoto"] = True
        searchquery = searchquery.exclude(foto='')

    if searchquery != None:
        workerid = []

        for elem in searchquery:
            workerid.append(elem.id)

        workerList = gerWorkList(idWorker=workerid, userAauthorized=userAauthorized)

    context["Workers"] = workerList
    context["searchProperty"] = searchProperty

    return context

def getServiceList(searchLine = None):

    serviceList = []
    querySet = Service.objects.all()

    if searchLine != None:
        querySet = querySet.filter(name__contains=searchLine)

    for e in querySet:
        serviceList.append({'id': e.id, 'name': e.name})

    return serviceList