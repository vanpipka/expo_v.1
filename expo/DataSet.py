from datetime import *
from main.models import *
import uuid
import base64

#from main.models import Comments

def setWorker(id, data):

    print("Сохраняем:")
    print(id)

    try:
        worker = Worker.objects.get(user_id=id)
    except:
        worker = Worker(user_id=id)

    print("Юзер:" + worker.name)

    if data.__contains__('name'):
        worker.name             = data.__getitem__('name')
    if data.__contains__('surname'):
        worker.surname          = data.__getitem__('surname')
    if data.__contains__('lastname'):
        worker.lastname         = data.__getitem__('lastname')
    if data.__contains__('Description'):
       worker.Description      = data.__getitem__('Description')
    if data.__contains__('education'):
        worker.education        = data.__getitem__('education')
    if data.__contains__('experience'):
        worker.experience       = data.__getitem__('experience')
    if data.__contains__('phonenumber'):
        worker.phonenumber      = data.__getitem__('phonenumber')
    if data.__contains__('emailaddress'):
        worker.emailaddress     = data.__getitem__('emailaddress')
    print(data.__contains__('city'))
    if data.__contains__('city'):
        worker.idCity           = City.objects.get(id=data.__getitem__('city'))

    #обработаем переданную дату начала работы
    if data.__contains__('experiencewith'):
        experiencewith = data.__getitem__('experiencewith')
        if experiencewith == '':
            worker.Experiencewith = datetime.datetime.now()
        else:
            try:
                worker.Experiencewith   = datetime.datetime.strptime(experiencewith, "%Y-%m-%d")
            except:
                print('ошибка при сохранении даты: ' + str(worker) + '/' + str(experiencewith))

    # Обработаем наличие ИП
    if data.__contains__('haveip'):
        haveIP = data.__getitem__('haveip')
        if haveIP == True:
            worker.haveIP = True
        else:
            worker.haveIP = False

    # Обработаем наличие инструмента
    if data.__contains__('haveinstrument'):
        haveinstrument = data.__getitem__('haveinstrument')
        if haveinstrument == True:
            worker.haveInstrument = True
        else:
            worker.haveInstrument = False

    # Обработаем разрешение на работу
    if data.__contains__('workpermit'):
        workpermit = data.__getitem__('workpermit')
        if workpermit == True:
            worker.workpermit = True
        else:
            worker.workpermit = False

    if data.__contains__('foto'):
        strOne = data.__getitem__('foto')

        fileurl = savefile(base64data=strOne, src='foto')

        if fileurl:
            worker.foto = fileurl

    if data.__contains__('files'):
        print("Обработка файлов=======================================")
        files = list(data.__getitem__('files'))
        for file in files:
            strOne = file['src']

            fileurl = savefile(base64data=strOne, src='attach')

            if fileurl:
                attach = WorkerAttachment()

                attach.Description  = file['description']
                attach.file         = fileurl

                attach.save()

                worker.WorkerAttachment.add(attach)

    #Сохраним
    worker.save()

    # Обработаем выбранные профессии
    worker.professions.clear()

    if data.__contains__('professions'):
        professions = list(data.__getitem__('professions'))

        for id_prof in professions:
            worker.professions.add(Professions.objects.get(id=id_prof))

    #обработаем указанные цены
    CostOfService.objects.filter(idWorker=worker).delete()
    if data.__contains__('servicelist'):

        servicelist = list(data.__getitem__('servicelist'))
        for service in servicelist:

            price       = service['price']
            idService   = service['id']

            if price != '':
                try:
                    costofservice = CostOfService(idWorker=worker, idService = Service.objects.get(id=idService))
                    costofservice.price = float(price)
                    costofservice.save()
                except:
                    print('ошибка при сохранении цены: '+str(worker)+'/'+str(idService))

    return

def refreshLastOnline(userId):

    try:
        worker = Worker.objects.get(user_id=userId)
        worker.lastOnline = datetime.datetime.now()
        worker.save()
    except:
        print("пользователь "+str(userId) + " не найден")

def savefile(base64data, src):

    if base64data.find('base64') == -1:
        return ''
    if base64data.find('image/') == -1:
        return ''

    d = base64data.partition(",")
    print("Фото======================================================================")

    strOne = d[2]
    strOne = strOne.encode()

    #                 #print('=====================================')
    #                #print(strOne)
    #               #pad = len(strOne) % 4
    #              #print('=====================================')
    #             #print(pad)
    strOne = b"=" + strOne

    directory = 'C:/djangoprojects/main/static/main/media/'
    name      = src+'/'+str(uuid.uuid4())+'.png'

    with open(directory+name, "wb") as fh:
        fh.write(base64.decodebytes(strOne.strip()))

    return name
