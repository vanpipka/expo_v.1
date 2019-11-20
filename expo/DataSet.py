from datetime import datetime as datet
from django.utils import timezone
from main.models import Worker, City, Country, Professions, WorkerAttachment, CostOfService, Service, UserType, Attacment
#from expo.SaveFile import savefile

def setWorker(id, data):

    print("Сохраняем:")
    print(id)

    worker = Worker.addWorker(user=id, type=1)

    print("Юзер: " + str(worker.id))

    if data.__contains__('name'):
        worker.name             = data.__getitem__('name')
    if data.__contains__('surname'):
        worker.surname          = data.__getitem__('surname')
    if data.__contains__('lastname'):
        worker.lastname         = data.__getitem__('lastname')
    if data.__contains__('description'):
       worker.Description      = data.__getitem__('description')
    if data.__contains__('education'):
        worker.education        = data.__getitem__('education')
    if data.__contains__('experience'):
        worker.experience       = data.__getitem__('experience')
    if data.__contains__('phonenumber'):
        worker.phonenumber      = data.__getitem__('phonenumber')
    if data.__contains__('salary'):
        if data.__getitem__('salary') == '':
            worker.salary = 0
        else:
            worker.salary = int(data.__getitem__('salary'))
    if data.__contains__('emailaddress'):
        worker.emailaddress     = data.__getitem__('emailaddress')
    #print(data.__contains__('city'))
    if data.__contains__('city') and data.__getitem__('city') != '':
        try:
            worker.idCity           = City.objects.get(id=data.__getitem__('city'))
        except:
            print('Не удалось сохранить город')
    #elif worker.idCity:
    #    worker.idCity = City.objects.get(id='00000000000000000000000000000000')

    #обработаем переданную дату начала работы
    if data.__contains__('experiencedate'):
        experiencewith = str(data.__getitem__('experiencedate'))
        if experiencewith == '':
            worker.Experiencewith = datet.now()
        else:
            try:
                worker.Experiencewith   = datet.strptime(experiencewith+"-01-01", "%Y-%m-%d")
            except:
                print('ошибка при сохранении даты: ' + str(worker) + '/' + str(experiencewith))

    #обработаем дату рождения
    if data.__contains__('birthday'):
        birthday = data.__getitem__('birthday')
        if birthday == '':
            try:
                worker.birthday = datet.strptime("1960-01-01", "%Y-%m-%d")
            except:
                print('ошибка при сохранении даты рождения: ' + str(worker) + '/1960-01-01')
        else:
            try:
                worker.birthday   = datet.strptime(birthday, "%Y-%m-%d")
            except:
                print('ошибка при сохранении даты рождения: ' + str(worker) + '/' + str(birthday))

    # Обработаем наличие ИП
    if data.__contains__('haveip'):
        haveIP = data.__getitem__('haveip')
        if haveIP == True:
            worker.haveIP = True
        else:
            worker.haveIP = False

    # Обработаем пол
    if data.__contains__('sex'):
        sex = data.__getitem__('sex')
        if sex == '1' or sex == 1:
            worker.sex = True
        else:
            worker.sex = False

    # Обработаем наличие инструмента
    if data.__contains__('haveinstrument'):
        haveinstrument = data.__getitem__('haveinstrument')
        if haveinstrument == True:
            worker.haveInstrument = True
        else:
            worker.haveInstrument = False

    # Обработаем готовность к командировкам
    if data.__contains__('readytotravel'):
        readytotravel = data.__getitem__('readytotravel')
        print('Готовность к командировкам:' + str(readytotravel))
        if readytotravel == True:
            worker.readytotravel = True
        else:
            worker.readytotravel = False

    # Обработаем подтверждение на обработку персоальных данных
    if data.__contains__('personaldataisallowed'):
        personaldataisallowed = data.__getitem__('personaldataisallowed')
        if personaldataisallowed == True:
            worker.personaldataisallowed = True
        else:
            worker.personaldataisallowed = False
    else:
        worker.personaldataisallowed = True

    # Обработаем разрешение на публикацию анкеты
    if data.__contains__('publishdata'):
        publishdata = data.__getitem__('publishdata')
        if publishdata == True:
            worker.publishdata = True
        else:
            worker.publishdata = False

    # Обработаем шенген
    if data.__contains__('haveshengen'):
        haveshengen = data.__getitem__('haveshengen')
        print('есть шенген:' + str(haveshengen))
        if haveshengen == True:
            worker.haveShengen = True
        else:
            worker.haveShengen = False

    # Обработаем загран пасспорт
    if data.__contains__('haveintpass'):
        haveintpass = data.__getitem__('haveintpass')
        print('есть загран пасспорт:' + str(haveintpass))
        if haveintpass == True:
            worker.haveIntPass = True
        else:
            worker.haveIntPass = False

    # Обработаем разрешение на работу
    if data.__contains__('workpermit'):
        workpermit = data.__getitem__('workpermit')
        print('workpermit:' + str(workpermit))
        if workpermit == True:
            worker.workpermit = True
        else:
            worker.workpermit = False

    # Обработаем национальность
    if data.__contains__('country'):
        print('country:' + str(country))
        country = Country.objects.get(id=data.__getitem__('country'))

        worker.nationality = country

        if country.workpermit:
            worker.workpermit = True

    if data.__contains__('fotourl'):
        strOne = data.__getitem__('fotourl')
        print('fotourl:')
        if strOne != None:

            fileurl = Attacment.savefile(base64data=strOne, src='foto', resizeit=True)

            if fileurl:
                worker.image = fileurl

        else:

            try:

                img = Attacment.objects.get(id='00000000000000000000000000000000')

            except:

                img = Attacment()

                img.id = '00000000000000000000000000000000'

                img.save()

            worker.image = img

    #Сохраним
    worker.save()

    # Обработаем выбранные профессии
    if data.__contains__('professions'):

        worker.professions.clear()

        professions = list(data.__getitem__('professions'))

        for id_prof in professions:
            try:
                if type(id_prof) == type({}):
                    worker.professions.add(Professions.objects.get(id=id_prof.get('id')))
                else:
                    worker.professions.add(Professions.objects.get(id=id_prof))
            except:
                print("не удалось сохранить профессию")

    if data.__contains__('delattachments'):
        delattachments = list(data.__getitem__('delattachments'))

        WorkerAttachment.objects.filter(id__in=delattachments).delete()

    # Обработаем файлы
    #if data.__contains__('attachments'):
     #   print("Обработка файлов=======================================")
     #   files = list(data.__getitem__('attachments'))
     #   for file in files:
     #       strOne = file['src']
#
     #       fileurl = savefile(base64data=strOne, src='attach', resizeit=True)
#
     #       if fileurl:
     #           attach = WorkerAttachment()
#
     #           attach.Description  = file['description']
     #           attach.file         = fileurl
     #           attach.resizeFile   = 'resize'+fileurl
     #           attach.save()
#
      #          worker.WorkerAttachment.add(attach)

    #обработаем указанные цены

    if data.__contains__('services'):
        CostOfService.objects.filter(idWorker=worker).delete()
        servicelist = list(data.__getitem__('services'))
        for service in servicelist:

            price       = service['price']
            idService   = service['id']

            if price != '' and price != '0' and price != 0:
                try:
                    costofservice = CostOfService(idWorker=worker, idService = Service.objects.get(id=idService))
                    costofservice.price = float(price)
                    costofservice.save()
                except:
                    print('ошибка при сохранении цены: '+str(worker)+'/'+str(idService))

    return

def refreshLastOnline(userId):

    try:

        el = UserType.GetElementByUser(userId)
        print(el)
        if el != None:
            el.lastOnline = timezone.now()
            el.save()

    except:
        print("пользователь "+str(userId) + " не найден")
