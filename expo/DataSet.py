from datetime import *
from main.models import *
import uuid

#from main.models import Comments

def setWorker(id, data, foto=''):

    print("Сохраняем:")
    print(id)

    try:
        worker = Worker.objects.get(user_id=id)
    except:
        worker = Worker(user_id=id)

    print("Юзер:" + worker.name)

    worker.name             = data.__getitem__('name')
    worker.surname          = data.__getitem__('surname')
    worker.lastname         = data.__getitem__('lastname')
    worker.Description      = data.__getitem__('Description')
    worker.education        = data.__getitem__('education')
    worker.experience       = data.__getitem__('experience')
    worker.phonenumber      = data.__getitem__('phonenumber')
    worker.emailaddress     = data.__getitem__('emailaddress')
    worker.haveIP           = False
    worker.workpermit       = False
    worker.idCity           = City.objects.get(id=data.__getitem__('idCity'))

    if foto != '':
        worker.foto         = foto

    #обработаем переданную дату начала работы
    experiencewith = data.__getitem__('Experiencewith')
    if experiencewith == '':
        worker.Experiencewith = datetime.datetime.now()
    else:
        try:
            experiencewith = datetime.datetime.strptime(experiencewith, "%Y-%m-%d")
            worker.Experiencewith   = experiencewith
        except:
            print('ошибка при сохранении даты: ' + str(worker) + '/' + str(experiencewith))

    # Обработаем наличие ИП
    if data.__contains__('haveIP'):
        haveIP = data.__getitem__('haveIP')

        if haveIP == 'True':
            worker.haveIP = True

    # Обработаем разрешение на работу
    if data.__contains__('workpermit'):
        workpermit = data.__getitem__('workpermit')

        if workpermit == 'True':
            worker.workpermit = True

    #Сохраним
    worker.save()

    # Обработаем выбранные профессии
    worker.professions.clear()

    if data.__contains__('Professions'):
        professions = data.getlist('Professions', {})

        for id_prof in professions:
            #try:
                worker.professions.add(Professions.objects.get(id=id_prof))
            #except:
            #    print('ошибка при сохранении профессии: ' + str(worker) + '/' + str(id_prof))

    #обработаем указанные цены
    CostOfService.objects.filter(idWorker=worker).delete()
    if data.__contains__('selectServices') and data.__contains__('inputServices'):

        selectServices  = data.getlist('selectServices', [])
        inputServices   = data.getlist('inputServices', [])

        i = 0
        while i < len(selectServices):
            id_service = selectServices[i]

            try:
                price   = inputServices[i]

                if price != '':
                    costofservice = CostOfService(idWorker=worker, idService = Service.objects.get(id=id_service))
                    costofservice.price = float(price)
                    costofservice.save()
            except:
                print('ошибка при сохранении цены: '+str(worker)+'/'+str(id_service))

            i += 1

    return

def refreshLastOnline(userId):

    try:
        worker = Worker.objects.get(user_id=userId)
        worker.lastOnline = datetime.datetime.now()
        worker.save()
    except:
        print("пользователь "+str(userId) + " не найден")


