from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models.signals import m2m_changed #, post_save
from django.db.models import Q
from django.utils import timezone
from django.dispatch import receiver
import datetime
import uuid
import base64
import random
from typing import Type
from PIL import Image
from django.conf import settings
from os import path
from expo.Balance import sendMessage
from expo.validate_uuid4 import validate_uuid4
import logging

logger = logging.getLogger(__name__)

class UserActivity(models.Model):

    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(datetime.date, default=None, null=True)

    def __str__(self):
        return str(self.user) + " - " + str(self.date)

    def setActivity(user):

        try:
            act = UserActivity.objects.get(date=datetime.datetime.now().date(), user=user)
        except Exception as e:
            act = UserActivity()
            act.user = user
            act.date = datetime.datetime.now().date()

            act.save()

class WorkGroup(models.Model):

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Professions(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    idWorkGroup = models.ForeignKey(WorkGroup, on_delete=models.CASCADE)
    indexName   = models.CharField(max_length=100)
    workerСount = models.DecimalField("Количество рабочих", max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        return self.name

    def setWorkerCount(self):

        print("Сохраняем количество по профессиям")
        cursor = connection.cursor()

        cursor.execute("SELECT main_professions.id, COUNT(main_worker.id) FROM main_professions LEFT JOIN main_worker_professions ON main_professions.id = main_worker_professions.professions_id LEFT JOIN main_worker ON main_worker.id = main_worker_professions.worker_id AND main_worker.publishdata GROUP BY main_professions.id")

        row = cursor.fetchall()

        for e in row:
            prof = Professions.objects.get(id=e[0])
            prof.workerСount = e[1]
            prof.save()

class Service(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    unit        = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Country(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    workpermit  = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Region(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    country     = models.ForeignKey(Country, on_delete=models.CASCADE, default='00000000000000000000000000000000')

    def __str__(self):
        return self.name

class City(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    indexName   = models.CharField(max_length=100)
    country     = models.ForeignKey(Country, on_delete=models.CASCADE, default='00000000000000000000000000000000')
    region      = models.ForeignKey(Region, on_delete=models.CASCADE, default='00000000000000000000000000000000')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.indexName = self.name.upper()
        super(City, self).save(*args, **kwargs)  # Call the "real" save() method.

class WorkerAttachment(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file        = models.FileField(null=True, blank=True, upload_to="media/attach/", verbose_name='Изображение')
    resizeFile  = models.FileField(null=True, blank=True, upload_to="media/resizeattach/", verbose_name='Изображение')
    Description = models.CharField(max_length=200)

class Attacment(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path        = models.FileField(null=True, blank=True, upload_to="media/attach/", verbose_name='Изображение')
    resizePath  = models.FileField(null=True, blank=True, upload_to="media/resizeattach/", verbose_name='Изображение')
    Description = models.CharField(max_length=200)

    def savefile(base64data, src = 'attacment', resizeit=False):

        if base64data.find('base64') != -1:

            if base64data.find('image/') == -1:
                return None
            d = base64data.partition(",")

            strOne = d[2]
            strOne = b"=" + strOne.encode()

        else:
            strOne = base64data

        your_media_root = '/opt/vseexpo/main/media/';#settings.MEDIA_ROOT
        directory       = str(your_media_root)
        name            = str(uuid.uuid4()) + '.png'
        fullpath        = path.join(directory, src, name)
        attachment      = Attacment()
        print("fullpath=============================================")
        print(fullpath)
        #try:
        if (True):
            print('1')
            with open(fullpath, "wb") as fh:
                b64decode = base64.b64decode(strOne.strip())
                fh.write(b64decode)
                attachment.path = fullpath.replace(directory, '').replace('\\', '/')
                print("attachment.path=============================================")
                print(attachment.path)
            if resizeit:
                resizename = str(uuid.uuid4()) + '.png'
                fullresizepath = path.join(directory, 'attacmentresize', resizename)
                Attacment.scale_image(input_image_path=fullpath, output_image_path=fullresizepath)
                attachment.resizePath = fullresizepath.replace(directory, '').replace('\\', '/')

        attachment.save()

        return attachment

    def scale_image(input_image_path,
                    output_image_path,
                    width=150,
                    height=150
                    ):

        original_image = Image.open(input_image_path)
        w, h = original_image.size
        if w > h:
            position = (w - h) / 2
            croped_image = original_image.crop((position, 0, w - position, h))
        elif h > w:
            position = (h - w) / 2
            croped_image = original_image.crop((0, position, w, h - position))
        else:
            croped_image = original_image

        if width and height:
            max_size = (width, height)
        elif width:
            max_size = (width, h)
        elif height:
            max_size = (w, height)
        else:
            # No width or height specified
            raise RuntimeError('Width or height required!')

        croped_image.thumbnail(max_size, Image.ANTIALIAS)
        croped_image.save(output_image_path)

        return output_image_path

    def getresizelink(attach):

        if attach.resizePath:

            if str(attach.resizePath)[0:1] =='/':
                img = str(settings.MEDIA_URL) + str(attach.resizePath)[1:]
            else:
                img = str(settings.MEDIA_URL) + str(attach.resizePath)

            print(img)

            return (img)
        else:
            return str(settings.STATIC_URL) + 'main/img/add-photo.png'

    def getlink(attach):
        if attach.path:

            if str(attach.path)[0:1] =='/':
                img = str(settings.MEDIA_URL) + str(attach.path)[1:]
            else:
                img = str(settings.MEDIA_URL) + str(attach.resizePath)

            return (img)
        else:
            return str(settings.STATIC_URL) + 'main/img/add-photo.png'

class Worker(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    #user_id     = models.OneToOneField(User, on_delete=models.CASCADE)
    block       = models.BooleanField(default=False) #Заблокирован
    name        = models.CharField(max_length=100, default="Не указано")
    surname     = models.CharField(max_length=100)
    nationality = models.ForeignKey(Country, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    education   = models.TextField()
    lastname    = models.CharField(max_length=100)
    haveIP      = models.BooleanField(default=False)
    haveShengen = models.BooleanField(default=False)
    haveIntPass = models.BooleanField(default=False) #ЗагранПаспорт
    readytotravel = models.BooleanField(default=False) #Готов к командировкам
    haveInstrument = models.BooleanField(default=False)
    fsocheck    = models.BooleanField(default=False)
    workpermit  = models.BooleanField(default=False)
    datacheck   = models.BooleanField(default=False)
    sex         = models.BooleanField(default=True)
    personaldataisallowed = models.BooleanField(default=False)
    publishdata = models.BooleanField(default=False)
    Description = models.TextField()
    idCity      = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    birthday    = models.DateField(datetime.date, default=None, null=True)
    Experiencewith = models.DateField(datetime.date, null=True)
    experience     = models.TextField()
    foto           = models.ImageField(null=True, blank=True, upload_to="media/", verbose_name='Изображение')
    image          = models.ForeignKey(Attacment, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    lastOnline     = models.DateTimeField("Последний онлайн", auto_now_add=True, null=True)
    professions    = models.ManyToManyField(Professions)
    phonenumber    = models.CharField(max_length=100)
    emailaddress   = models.CharField(max_length=100)
    #WorkerAttachment    = models.ManyToManyField(WorkerAttachment)
    salary              = models.DecimalField(max_digits=10, decimal_places=0, default=0) #Цена основной работы

    def __str__(self):
        return self.name

    def SetAdminData(data):

        try:
            worker = Worker.objects.get(id = data.get("id"))

            worker.block = data.get("block")
            #worker.fsocheck = data.get("fsocheck")
            worker.datacheck = data.get("datacheck")

            worker.save()

        except:
            print('не удалось сохранить работника')

    # < QueryDict: {'data': [
    #     '{"id":"29beee02-7b25-4314-b110-3042c67db300","datacheck":true,"fsocheck":false,"block":true}'],
    #               'csrfmiddlewaretoken': ['NpjIHZBxP1EDbEzjtaQ1XwBZRN4DJrDbDc5d98ic0eMgkjDpoas6TtDyOTZN4imR']} >

    def getWorkerQueryByUser(user):
        userList = UserType.objects.all().filter(user=user, type=1).values('worker')

        return Worker.objects.all().filter(id__in=userList)

    def addWorker(user, type):

        if type != 1:
            return False

        workerQuerySet = Worker.getWorkerQueryByUser(user)

        if workerQuerySet.count() == 0:
            worker = Worker()
            worker.phonenumber = user.username
            worker.personaldataisallowed = True
            worker.save()
            UserType.AddUserType(worker = worker, user=user, type=type, company=None)
            return worker
        else:
            return workerQuerySet[0]

    def getWorkerRating(worker):

        ratingList = {"rating": 0, "commentsCount": 0}

        try:
            workerRating = WorkerRating.objects.get(idWorker=worker)
            ratingList["rating"] = workerRating.rating
            ratingList["commentsCount"] = workerRating.commentsCount

        except:
            print("рейтинг для " + str(worker) + " не найден")

        return ratingList

    def GetElement(id):

        elem = None

        try:

            elem = Worker.objects.get(id=id)

        except:

            print('не удалось получить работника по id')

        return elem

class Company(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name            = models.CharField(max_length=100, default="Не указано")
    vatnumber       = models.CharField(max_length=10)
    foto            = models.ImageField(null=True, blank=True, upload_to="img/", verbose_name='Изображение')
    image           = models.ForeignKey(Attacment, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    phonenumber     = models.CharField(max_length=100)
    emailaddress    = models.CharField(max_length=100)
    description     = models.TextField()
    idCity          = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    block           = models.BooleanField(default=False)

    lastOnline      = models.DateTimeField("Последний онлайн", auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    def getCompanyQueryByUser(user):

        userList = UserType.objects.all().filter(user=user, type=2).select_related('idCity').values('company')

        return Company.objects.all().filter(id__in=userList)

    def GetCompanyByUser(user):

        queryList = Company.getCompanyQueryByUser(user)

        if queryList.count() == 0:
            print('Не найдено компании')
            return {}

        else:

            companyObject = queryList[0]

            company = {'name': companyObject.name,
                        'vatnumber': companyObject.vatnumber,
                        'fotourl': Attacment.getlink(companyObject.image),
                        'resizefotourl': Attacment.getresizelink(companyObject.image),
                        'phonenumber': companyObject.phonenumber,
                        'emailaddress': companyObject.emailaddress,
                        'description': companyObject.description,
                        'city': {"id": companyObject.idCity.id, "name": companyObject.idCity.name}}

            return company

    def UpdateCompany(user, data):

        queryList = Company.getCompanyQueryByUser(user)

        if queryList.count() != 0:

            company = queryList[0]

            company.name            = data.get('name', '')
            company.vatnumber       = data.get('vatnumber', '')
            company.phonenumber     = data.get('phonenumber', '')
            company.emailaddress    = data.get('emailaddress', '')
            company.description     = data.get('description', '')

            if data.__contains__('city') and data.get('city', '') != '':
                try:
                    company.idCity = City.objects.get(id=data.__getitem__('city'))
                except:
                    company.idCity = City.objects.get(id='00000000000000000000000000000000')
            elif company.idCity:
                company.idCity = City.objects.get(id='00000000000000000000000000000000')

            if data.__contains__('fotourl'):
                strOne = data.__getitem__('fotourl')

                fileurl = Attacment.savefile(base64data=strOne, src='foto', resizeit=True)

                if fileurl:
                    company.image = fileurl

            company.save()

    def addCompany(user, type):

        if type != 2:
            return False

        companyQuerySet = Company.getCompanyQueryByUser(user)

        if companyQuerySet.count() == 0:
            company = Company()
            company.phonenumber = user.username
            company.save()
            UserType.AddUserType(company = company, user=user, type=type, worker=None)
            return company
        else:
            return companyQuerySet[0]

    def SetAdminData(data):

        try:
            company = Company.objects.get(id = data.get("id"))

            company.block = data.get("block")

            company.save()

        except:
            print('не удалось сохранить компанию')

    def GetElement(id):

        elem = None

        try:

            elem = Company.objects.get(id=id)

        except:

            print('не удалось получить работника по id')

        return elem

class News(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    description = models.TextField()
    created     = models.DateTimeField("Дата добавления", default=timezone.now)
    link        = models.CharField(max_length=100)
    image       = models.CharField(max_length=100)
    block       = models.BooleanField(default=False)
    imagelink   = models.ForeignKey(Attacment, on_delete=models.CASCADE, default="00000000000000000000000000000000")

    def __str__(self):
        return self.name

    def GetActual(self, position_begin=None, position_end=None):

        objects = News.objects.all().filter(block=False).order_by("-created")

        if position_begin != None and position_end != None:
            objects = objects[position_begin: position_end]

        objects = list(objects.values('id', 'name', 'description', 'link', 'imagelink', 'created'))

        for e in objects:

            print(e['imagelink'])

            if e['imagelink']:
                e['image'] = Attacment.getresizelink(Attacment.objects.get(id=e['imagelink']))

        return objects

    def SetAdminData(data):

        try:
            worker = News.objects.get(id = data.get("id"))

            worker.block = data.get("block")

            worker.save()

        except:
            print('не удалось сохранить работника')

    def SaveResponse(user, data):

        if user.is_superuser:
            #try:
                news = News()

                news.name           = data.get('name', '')
                news.description    = data.get('description', '')
                news.link           = data.get('link', '')

                if data.__contains__('fotourl'):
                    strOne = data.__getitem__('fotourl')

                    if strOne != None:

                        fileurl = Attacment.savefile(base64data=strOne, src='foto', resizeit=True)

                        if fileurl:
                            news.imagelink = fileurl

                    else:

                        try:

                            img = Attacment.objects.get(id='00000000000000000000000000000000')

                        except:

                            img = Attacment()

                            img.id = '00000000000000000000000000000000'

                            img.save()

                            news.image = img

                news.save()

            #except:
            #    print('не удалось сохранить новость')
            #    return False
        else:
            return False

        return True

class JobOrder(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    created     = models.DateTimeField("Дата добавления", auto_now_add=True)
    date        = models.DateTimeField("Дата проведения работ", default=datetime.date(1900, 1, 1))
    enddate     = models.DateTimeField("Дата окончания работ", default=datetime.date(1900, 1, 1))
    place       = models.CharField(max_length=100)
    company     = models.ForeignKey(Company, on_delete=models.CASCADE)
    city            = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    responseCount   = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    deleted         = models.BooleanField(default=False)
    author          = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.description

    def GetActual(self, user=None):

        response_array = []
        userType       = 0

        if User != None:

            userType = UserType.GetUserType(user)

            if userType == 1:

                worker = UserType.GetElementByUser(user)

                response_list = list(JobResponse.objects.filter(worker=worker).values('jobOrder_id'))

                for e in response_list:
                    if response_array.count(e['jobOrder_id']) == 0:
                        response_array.append(e['jobOrder_id'])

        objects = list(JobOrder.objects.all().filter(deleted=False).select_related('city').select_related('company').order_by("-created").values('id', 'deleted', 'responseCount', 'description', 'date', 'enddate', 'place', 'created', 'company', 'city', 'city_id', 'city__name', 'company__name', 'company__image'))

        id_jobs = []

        for e in objects:
            id_jobs.append(e['id'])

        #print(id_jobs)

        jobComposition = list(JobComposition.objects.all().filter(jobOrder_id__in=id_jobs).select_related('profession').values('jobOrder_id', 'profession__id', 'profession__name', 'count', 'price'))

        for e in objects:

            try:
                e['photo'] = Attacment.getresizelink(Attacment.objects.get(id=e['company__image']))
            except:
                e['photo'] = '';

            if (userType != 1):
                e['response_is_available'] = 2      #ничего не выводить
            elif (response_array.count(e['id'])) == 0:
                e['response_is_available'] = 1      #Можно откликнуться
            else:
                e['response_is_available'] = 0      #уже откликнулся

            e['job_composition'] = []

            for j in jobComposition:
                if j['jobOrder_id'] == e['id']:
                    e['job_composition'].append(j)

        return objects

    def GetInfo(self, id, user=None):

        response_array = []
        userType       = 0

        if validate_uuid4(id) != True:
            return False

        if User != None:
            if User.is_active:

                userType    = UserType.GetUserType(user)
                worker      = UserType.GetElementByUser(user)
                response    = {"response_is_available": 1}

                objects = list(JobOrder.objects.filter(id=id).select_related('city').select_related('company').order_by("-created").values('author', 'id', 'responseCount', 'description', 'enddate', 'date', 'place', 'created', 'company', 'city', 'city_id', 'city__name', 'company__name', 'company__image'))

                if len(objects) == 0:
                    return False

                e = objects[0]

                response_list = list(JobResponse.objects.filter(jobOrder_id = id).select_related('worker').values('id', 'answer', 'worker', 'worker__name', 'worker__image', 'worker__id', 'status', 'created'))

                for responses in response_list:

                    status = {'value': responses['status']}

                    if responses['status'] == 0:
                        status['name'] = 'Отклик не просмотрен'
                    elif responses['status'] == 1:
                        status['name'] = 'Приглашение'
                    elif responses['status'] == 2:
                        status['name'] = 'Отказано'
                    else:
                        status['name'] = ''

                    if e['author'] == user:
                        status['edit']: True
                    else:
                        status['edit']: False

                    if responses['worker'] == worker.id:

                        response['status']                  = responses['status']
                        response['response_is_available']   = 0

                        if responses['status'] == 0:
                            response['name'] = 'Отклик отправлен'
                        elif responses['status'] == 1:
                            response['name'] = 'Вас пригласили'
                        elif responses['status'] == 2:
                            response['name'] = 'Вам отказано'
                        else:
                            response['name'] = 'Откликнуться'

                    data = {'id': responses['id'],
                                'description' : responses['answer'],
                                'worker': responses['worker__name'],
                                'photo': Attacment.getresizelink(Attacment.objects.get(id=responses['worker__image'])),
                                'workerurl': '/worker/info?id='+str(responses['worker__id']),
                                'created': responses['created'],
                                'status': status}

                    response_array.append(data)

        jobComposition = list(JobComposition.objects.all().filter(jobOrder_id=id).select_related('profession').values('jobOrder_id', 'profession__id', 'profession__name', 'count', 'price'))

        try:
            e['photo'] = Attacment.getresizelink(Attacment.objects.get(id=e['company__image']))
        except:
            e['photo'] = '';

        if (userType != 1):
            e['response_is_available'] = 2      #ничего не выводить

        e['response'] = response

        e['job_composition'] = []

        for j in jobComposition:
            if j['jobOrder_id'] == e['id']:
                e['job_composition'].append(j)

        e['response_array'] = response_array

        return e

    def SaveResponse(user, data):

        userType = UserType.GetUserType(user)

        if userType == 1:

            try:

                jobResponse = JobResponse()

                jobResponse.jobOrder = JobOrder.objects.get(id=data['job_id'])
                jobResponse.worker   = UserType.GetElementByUser(user)
                jobResponse.answer   = data.get('job_description', 'Сопроводительного письма нет')
                jobResponse.save()

                MessageExpo.SaveJobResponse(jobResponse, userType)

            except:

                return False

            return True

        else:

            return False

    def SaveOrder(user, data):

        userType = UserType.GetUserType(user)

        if userType == 2 or user.is_superuser:

            try:
                print(1)
                id = data.get('job_id', '')
                print(id)

                if id != '':
                    print(2)
                    if validate_uuid4(id):
                        print(3)
                        jobOrder = JobOrder.objects.get(id=id)

                        if jobOrder.author != user and user.is_superuser == False:
                            print(6)
                            return False
                    else:
                        return False
                else:
                    print(4)
                    jobOrder = JobOrder()

                print(5)

                jobOrder.description    = data.get('job_description', '')
                jobOrder.deleted        = data.get('job_deleted', False)
                if id == '':
                    jobOrder.company        = UserType.GetElementByUser(user)
                    jobOrder.author         = user

                print(7)
                id_city = data.get('job_city', '00000000000000000000000000000000')

                if id_city == '':
                    id_city = '00000000000000000000000000000000'

                jobOrder.city = City.objects.get(id=id_city)

                try:
                    jobOrder.date = datetime.datetime.strptime(data.get('job_date', "1960-01-01"), "%Y-%m-%d")
                except:
                    print('ошибка при сохранении даты начала работ: ' + str(jobOrder) + '/1960-01-01')

                try:
                    jobOrder.enddate = datetime.datetime.strptime(data.get('job_enddate', "1960-01-01"), "%Y-%m-%d")
                except:
                    print('ошибка при сохранении даты окончания работ: ' + str(jobOrder) + '/1960-01-01')

                jobOrder.save()

                JobComposition.objects.filter(jobOrder=jobOrder).delete()

                job_composition = data.get('job_composition', [])

                for e in job_composition:

                    if e.get('id', ''):

                        Composition = JobComposition()

                        Composition.jobOrder = jobOrder
                        Composition.profession = Professions.objects.get(id=e.get('id', ''))
                        Composition.count = int(e.get('count', 0))
                        Composition.price = int(e.get('price', 0))

                        Composition.save()

            except:

                return False

            return True

        else:

            return False

class JobComposition(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobOrder    = models.ForeignKey(JobOrder, on_delete=models.CASCADE)
    profession  = models.ForeignKey(Professions, on_delete=models.CASCADE)
    count       = models.DecimalField(max_digits=2, decimal_places=0, default=0)
    price       = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        return self.id

class JobResponse(models.Model):

    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobOrder = models.ForeignKey(JobOrder, on_delete=models.CASCADE)
    worker   = models.ForeignKey(Worker, on_delete=models.CASCADE)
    answer   = models.TextField()
    created  = models.DateTimeField("Дата добавления", auto_now_add=True)
    status   = models.DecimalField(max_digits=1, decimal_places=0, default=0)
    #0-новый, 1-принят, 2-отказ

    def save(self, *args, **kwargs):

        super(JobResponse, self).save(*args, **kwargs)  # Call the "real" save() method.

        self.jobOrder.responseCount = len(JobResponse.objects.filter(jobOrder = self.jobOrder).values('id'))
        self.jobOrder.save()

    def getCount(user):

        company = UserType.GetElementByUser(user);
        response_list = list(JobResponse.objects.filter(jobOrder__company=company).filter(status=0))

        return len(response_list)

    def getActualForCompany(user):

        company = UserType.GetElementByUser(user);

        response_array = []

        response_list = list(JobResponse.objects.filter(jobOrder__company=company).order_by("-created").select_related('jobOrder__company').values(
            'id', 'status', 'created', 'answer', 'jobOrder_id', 'worker_id', 'worker__name', 'worker__image'))

        for e in response_list:

            status = {'value': e['status']}

            if e['status'] == 0:
                status['name'] = 'Отклик не просмотрен'
            elif e['status'] == 1:
                status['name'] = 'Приглашение'
            elif e['status'] == 2:
                status['name'] = 'Отказано'
            else:
                status['name'] = ''

            response_array.append({'id': e['id'],
                                    'jobOrder': '/jobs/info/?id='+str(e['jobOrder_id']),
                                    'description':  e['answer'],
                                    'created':  e['created'],
                                    'status':   status,
                                    'company': {'url': '/worker/info/?id='+str(e['worker_id']), 'name': e['worker__name'], 'photo': Attacment.getresizelink(Attacment.objects.get(id=e['worker__image']))},

                                    })

        return response_array

    def getActualForWorker(user):

        worker = UserType.GetElementByUser(user);
        response_array = []

        response_list = list(JobResponse.objects.filter(worker=worker).order_by("-created").select_related('jobOrder').select_related('jobOrder__company').values(
            'id', 'status', 'created', 'jobOrder__description', 'jobOrder_id', 'jobOrder__company_id', 'jobOrder__company', 'jobOrder__company__name', 'jobOrder__company__image'))

        for e in response_list:

            status = {'value': e['status']}

            if e['status'] == 0:
                status['name'] = 'Отклик не просмотрен'
            elif e['status'] == 1:
                status['name'] = 'Приглашение'
            elif e['status'] == 2:
                status['name'] = 'Отказано'
            else:
                status['name'] = ''

            response_array.append({'id': e['id'],
                                    'jobOrder': '/jobs/info/?id='+str(e['jobOrder_id']),
                                    'description':  e['jobOrder__description'],
                                    'created':  e['created'],
                                    'status':   status,
                                    'company': {'url': '/company/?id='+str(e['jobOrder__company_id']), 'name': e['jobOrder__company__name'], 'photo': Attacment.getresizelink(Attacment.objects.get(id=e['jobOrder__company__image']))},

                                    })

        return response_array

class UserType(models.Model):

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    type    = models.DecimalField(max_digits=2, decimal_places=0)   #2-компания, 1-специалист
    worker  = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def AddUserType(company, worker, user, type):

        try:
            userType = UserType.objects.get(user=user)

            if type == 1 or type == None:
                userType.worker     = worker
                userType.company    = None
                userType.type       = 1
            else:
                userType.worker = None
                userType.company = company
                userType.type = 2

            userType.save()

        except ObjectDoesNotExist:

            if type == 1 or type == None:
                userType = UserType(worker=worker, user=user, type=1)
            else:
                userType = UserType(company=company, user=user, type=type)

            userType.save()

        return userType

    def SetUserType(user, type):

        print(type)

        try:
            userType = UserType.objects.get(user=user)
            userType.type = type
            userType.save()

        except ObjectDoesNotExist:

            if type == 1 or type == None:
                Worker.addWorker(user, 1)
            else:
                Company.addCompany(user, 2)

    def GetUserType(user):

        try:
            userType = UserType.objects.get(user=user)

            return userType.type

        except ObjectDoesNotExist:

            return None

    def GetUserFromWorker(worker):

        user = None

        try:

            user = UserType.objects.get(worker=worker).user

        except:

            print('не удалось получить пользователя по работнику')

        return user

    def GetUserFromCompany(company):

        user = None

        try:

            user = UserType.objects.get(company=company).user

        except:

            print('не удалось получить пользователя по компании')

        return user

    def GetElementByUser(user):

        elem = None

        try:
            element = UserType.objects.get(user=user)

            if element.type == 1:
                elem = element.worker
            else:
                elem = element.company

        except ObjectDoesNotExist:
            print('не удалось получить запись userType '+str(user))

        return elem

    def GetUserByID(id):

        elem = None

        if validate_uuid4(id):

            element = UserType.objects.all().filter(Q(worker=id) | Q(company=id))

            if element.count() != 0:

                elem = element[0].user

        return elem

class ConfirmCodes(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phoneNumber = models.CharField(max_length=100)
    code        = models.CharField(max_length=4)

    def GetCode(phoneNumber):

        try:

            code = ConfirmCodes.objects.all().get(phoneNumber=phoneNumber).code

        except:

            code = str(random.randint(10000, 99999))

        return code

    def AddCode(phoneNumber, send = False):

        print("AddCode")

        phoneNumber = phoneNumber.replace(' ', '')
        phoneNumber = phoneNumber.replace(')', '')
        phoneNumber = phoneNumber.replace('(', '')
        phoneNumber = phoneNumber.replace('-', '')
        phoneNumber = phoneNumber.replace('+7', '8')

        confirmcode = str(random.randint(1000, 9999))

        print("Отправляем смс: ")
        print("Номер: "+str(phoneNumber))
        print("Код: "+str(confirmcode))

        obj, created = ConfirmCodes.objects.all().get_or_create(phoneNumber=phoneNumber, defaults={'phoneNumber': phoneNumber, 'code': confirmcode})

        obj.code = confirmcode
        obj.save()

        if send == True:
            text = 'Код подтверждения для завершения регистрации: ' + str(confirmcode)
            dd = sendMessage(phone=phoneNumber, text=text)

    def SendLink(phoneNumber, type):

        print("SendLink")

        phoneNumber = phoneNumber.replace(' ', '')
        phoneNumber = phoneNumber.replace(')', '')
        phoneNumber = phoneNumber.replace('(', '')
        phoneNumber = phoneNumber.replace('-', '')
        phoneNumber = phoneNumber.replace('+7', '8')

        if type == '1':
            text = 'Ссылка для загрузки VseEXPO: https://apps.apple.com/ru/app/vseexpo/id1481122024'
        elif type == '2':
            text = 'Ссылка для загрузки VseEXPO: https://play.google.com/store/apps/details?id=com.vseexpo.app'
        else:
            return

        dd = sendMessage(phone=phoneNumber, text=text)

class CostOfService(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idService   = models.ForeignKey(Service, on_delete=models.CASCADE)
    idWorker    = models.ForeignKey(Worker, on_delete=models.CASCADE)
    price       = models.DecimalField(max_digits=10, decimal_places=0)

class Comments(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idUser      = models.ForeignKey(User, related_name="User", verbose_name="Пользователь", on_delete=models.CASCADE)
    idWorker    = models.ForeignKey(Worker, related_name="Worker", verbose_name="Работник", on_delete=models.CASCADE)
    idProf      = models.ForeignKey(Professions, verbose_name="Работа", on_delete=models.CASCADE)
    text        = models.TextField("Комментарий")
    created     = models.DateTimeField("Дата добавления", auto_now_add=True, null=True)
    moderation  = models.BooleanField("Модерация", default=False)
    rating      = models.DecimalField("Оценка", max_digits=1, decimal_places=0)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return "{}".format(self.idUser)

    def save(self, *args, **kwargs):
        super(Comments, self).save(*args, **kwargs)  # Call the "real" save() method.
        Comments.setRating(self)
        MessageExpo.saveComment(self)

    def setRating(comment):

        rating = Comments.objects.all().filter(idWorker=comment.idWorker).filter(moderation=True).aggregate(models.Avg('rating'), models.Count('id'))
        WorkerRating.updateRating(comment.idWorker, rating)

        #print("Количество:" +str(commentCount)+ " среднее:" + str(rating))

    def GetActual(self, position_begin=None, position_end=None):

        objects = Comments.objects.all().filter(moderation=True).select_related("Worker").filter(rating__gte=3).order_by("-created")

        if position_begin != None and position_end != None:
            objects = objects[position_begin: position_end]

        objects = list(objects.values('idWorker_id', 'idWorker__name', 'idWorker__surname', 'idWorker__image', 'text'))

        for e in objects:

            ratingInfo = Worker.getWorkerRating(e['idWorker_id'])
            e['rating'] = ratingInfo['rating']

            e['idWorker__image'] = Attacment.getresizelink(Attacment.objects.get(id = e['idWorker__image']))

        return objects

    def SetAdminData(data):

        try:
            comment = Comments.objects.get(id = data.get("id"))

            comment.moderation = data.get("moderation")

            comment.save()

        except:
            print('не удалось сохранить компанию')

class Message(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender          = models.ForeignKey(User, related_name= "Отправитель", verbose_name="Отправитель", on_delete=models.CASCADE)
    recipient       = models.ForeignKey(User, related_name= "Получатель", verbose_name="Получатель", on_delete=models.CASCADE)
    text            = models.TextField("Текст")
    subject         = models.TextField("Тема")
    read            = models.BooleanField("Прочитано", default=False)
    created         = models.DateTimeField("Дата добавления", auto_now_add=True, null=True)
    comment         = models.ForeignKey(Comments, verbose_name="ссылка на комментарий", on_delete=models.CASCADE, null=True)
    jobresponse     = models.ForeignKey(JobResponse, verbose_name="ссылка на отклик", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.id

    def GetActualCount(user):

        count = 0

        if user.is_authenticated:

            count = Message.objects.all().filter(recipient=user).filter(read=False).aggregate(models.Avg('recipient'), models.Count('id')).get('id__count', 0)

        return count

    def GetAll(user, who=''):

        messageList = []

        print('RNJ:'+who)

        #if who != '':

        #    idList = []

        #    message1 = Message.objects.all().filter(sender=user).filter(recipient=who).values('id')
        #    message2 = Message.objects.all().filter(recipient=user).filter(sender=who).values('id')

        #    for e in message1:
        #        idList.append(e.get('id'))
        #    for e in message2:
        #        idList.append(e.get('id'))

        #    print(idList)

        #    messageQuery = Message.objects.all().filter(id__in = idList)

        #else:

        messageQuery = Message.objects.all().filter(Q(recipient=user) | Q(sender=user))

        messageQuery = messageQuery.select_related('comment').select_related('jobresponse').order_by("-created")
        #messageQuery = Message.objects.all().select_related('comment').select_related('jobresponse').order_by("-created")

        for e in messageQuery:

            sender = UserType.GetElementByUser(e.sender)

            #print(type(sender))

            if type(sender) == Worker:
                url = '/worker/info?id='+str(sender.id)
            else:
                url = '/company?id='+str(sender.id)

            message = {'id': e.id, 'date': e.created, 'theme': e.subject, 'sender': {'name': sender.name, 'foto': Attacment.getresizelink(sender.image), 'url': url}}

            if e.comment != None:
                message['text'] = e.comment.text
            elif e.jobresponse != None:
                message['text'] = e.jobresponse.answer
            else:
                message['text'] = e.text

            messageList.append(message)

            if e.read == False:
                e.read = True
                e.save()

        return messageList

    def GetAllDialogs(user):

        messageList = []
        dialogList  = []

        #messageQuery = Message.objects.all().filter(recipient=user).select_related('comment').select_related('jobresponse').order_by("-created")
        #messageQuery = Message.objects..select_related('comment').select_related('jobresponse').order_by("-created")


        recipient = Message.objects.all().filter(Q(recipient=user) | Q(sender=user)).values('recipient').distinct();
        sender    = Message.objects.all().filter(Q(recipient=user) | Q(sender=user)).values('sender').distinct();

        for r in recipient:

            dialogList.append(r.get('recipient'))

        for s in sender:

            if dialogList.count(s.get('sender')) == 0:
                 dialogList.append(s.get('sender'))

        for e in dialogList:

            sender = UserType.GetElementByUser(e)

            #print(type(sender))

            if type(sender) == Worker:
                url = '/worker/info?id='+str(sender.id)
            else:
                url = '/company?id='+str(sender.id)

            message = {'id': sender.id, 'name': sender.name, 'foto': Attacment.getresizelink(sender.image), 'url': url}

            #if e.comment != None:
            #    message['text'] = e.comment.text
            #elif e.jobresponse != None:
            #    message['text'] = e.jobresponse.answer
            #else:
            #    message['text'] = e.text

            messageList.append(message)

            #if e.read == False:
            #    e.read = True
            #    e.save()

        return messageList

    def SaveNewMessage(Content, User):

        print(Content)

        message = Message()

        recipient_type = Content.get('resipient_type')

        if recipient_type == '1':
            message.recipient   = UserType.GetUserFromWorker(Worker.GetElement(Content.get('resipient_id')))
        elif recipient_type == '2':
            message.recipient   = UserType.GetUserFromCompany(Company.GetElement(Content.get('resipient_id')))
        else:
            return False

        if message.recipient != None:

            message.sender      = User
            message.text        = Content.get('text')
            message.subject     = Content.get('theme')

            message.save()

            return True

        return False

    def SaveComment(Comment):

        recipient = UserType.GetUserFromWorker(worker=Comment.idWorker)

        if recipient != None:

            message = Message()

            message.sender      = Comment.idUser
            message.recipient   = recipient
            message.subject     = 'Добавлен новый отзыв'
            message.comment     = Comment

            message.save()

class WorkerRating(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idWorker        = models.ForeignKey(Worker, verbose_name="Работник", on_delete=models.CASCADE)
    rating          = models.DecimalField("Оценка", max_digits=3, decimal_places=2)
    commentsCount   = models.DecimalField("Количество комментариев", max_digits=10, decimal_places=0)

    def updateRating(worker, rating):

        try:
            workerRating = WorkerRating.objects.get(idWorker=worker)
        except:
            workerRating = WorkerRating(idWorker=worker)

        if (rating['rating__avg'] == None):
            workerRating.rating         = 0;
        else:
            workerRating.rating         = rating['rating__avg']

        if (rating['id__count'] == None):
            workerRating.commentsCount  = 0;
        else:
            workerRating.commentsCount  = rating['id__count']

        workerRating.save()

class DialogManager(models.Manager):
    def create_dialog(self, data):

        dialog = self.create(idUser1  = data['user1'],
                            idUser2    = data['user2'],
                            )
        # do something with the book
        return dialog

class Dialog(models.Model):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idUser1        = models.ForeignKey(User, related_name="Участник_1", verbose_name="Участник_1", on_delete=models.CASCADE)
    idUser2        = models.ForeignKey(User, related_name="Участник_2", verbose_name="Участник_2", on_delete=models.CASCADE)
    lastMessage    = models.ForeignKey('MessageExpo', blank = True, related_name="Последнее_сообщение", verbose_name="Последнее_сообщение", null=True, on_delete=models.CASCADE)

    objects        = DialogManager()

    def __str__(self):
        return str(self.id) +': '+ self.idUser1.username + '-' + self.idUser2.username

    def GetCurrentDialog(dialogID):

        try:
            return (Dialog.objects.get(id=dialogID))
        except Exception as e:
            return None

    def GetDialog(user1, user2):

        if user1 == user2:
            return None

        dialog = Dialog.objects.all().filter(Q(idUser1=user1, idUser2=user2) | Q(idUser1=user2, idUser2=user1))

        if dialog.count() == 0:
            data = {'user1': user1, 'user2': user2}

            try:
                newDialog = Dialog.objects.create_dialog(data)
            except:
                newDialog = None

        else:
            newDialog = dialog[0]

        return newDialog

    def GetDialogs(user):

        dialogList  = []
        dialogs = Dialog.objects.all().filter(Q(idUser1=user) | Q(idUser2=user)).select_related('lastMessage').order_by('-lastMessage__created')

        for d in dialogs:

            lastMessage = {}

            if d.lastMessage != None:
                lastMessage['date'] = d.lastMessage.created.strftime("%d.%m.%Y %H:%M")
                lastMessage['text'] = d.lastMessage.text

            if (user == d.idUser1):
                sender = UserType.GetElementByUser(d.idUser2)
            else:
                sender = UserType.GetElementByUser(d.idUser1)


            url = '/dialogs?id='+str(d.id)

            message = {'id': d.id,
                        'url': url,
                        'sender': {'name': sender.name, 'foto': Attacment.getresizelink(sender.image)},
                        'lastMessage': lastMessage
                    }

            dialogList.append(message)

        return dialogList

    def ThereIsAccessToTheDialog(user, dialogID):

        data = Dialog.objects.all().filter(id = dialogID).filter(Q(idUser1=user) | Q(idUser2=user))

        return data.count() != 0

    def refreshLastMessage(message):

        try:
            dialog = message.idDialog;
            dialog.lastMessage = message
            dialog.save()
        except Exception as e:

            print('не удалось обновить последнее сообщение диалога')

class MessageExpoManager(models.Manager):
    def create_message(self, data):

        message = self.create(idDialog  = data['idDialog'],
                            text        = data['text'],
                            sender      = data['sender'],
                            recipient   = data['recipient']
                            )
        # do something with the book
        return message

class MessageExpo(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idDialog        = models.ForeignKey(Dialog, related_name= "Dialog", verbose_name="Dialog", on_delete=models.CASCADE)
    sender          = models.ForeignKey(User, related_name= "ОтправительСообщения", verbose_name="Отправитель", on_delete=models.CASCADE)
    recipient       = models.ForeignKey(User, related_name= "ПолучательСообщения", verbose_name="Получатель", on_delete=models.CASCADE)
    text            = models.TextField("Текст")
    subject         = models.TextField("Тема")
    order           = models.ForeignKey(JobOrder, related_name= "Order", verbose_name="JobOrder", on_delete=models.CASCADE, null=True)
    read            = models.BooleanField("Прочитано", default=False)
    created         = models.DateTimeField("Дата добавления", default=timezone.now)

    objects         = MessageExpoManager()

    def __str__(self):
        return self.sender.username + '-' + self.recipient.username + ': '+self.subject

    def save(self, *args, **kwargs):
        super(MessageExpo, self).save(*args, **kwargs)  # Call the "real" save() method.

        Dialog.refreshLastMessage(self)

    def getMessagesByDialog(user, idDialog=''):

        answer = {'status': False, 'dialogID': idDialog}

        if validate_uuid4(idDialog):
            if Dialog.ThereIsAccessToTheDialog(user, idDialog):
                dialog = Dialog.GetCurrentDialog(idDialog)

                if dialog != None:
                    answer['status'] = True
                    answer['companion'] = UserType.GetElementByUser(dialog.idUser2 if user == dialog.idUser1 else dialog.idUser1).name
                    answer['messageList'] = []

                    messageList = MessageExpo.objects.all().filter(idDialog = idDialog).order_by('created')

                    for m in messageList:
                        answer['messageList'].append({'id': str(m.id),
                                                    'text': m.text,
                                                    'subject': m.subject,
                                                    'itsMe': True if user == m.sender else False,
                                                    'created': m.created.strftime("%d.%m.%Y %H:%M"),
                                                    })

                        if m.read == False and m.recipient == user:
                            m.read = True
                            m.save()

                else:

                    answer['message'] = 'is not valid GUID'

            else:

                answer['message'] = 'Доступ  запрещен'

        else:
            answer['message'] = 'is not valid GUID'

        return answer

    def addMessageToDialog(user, data):

        dialogID = data.get('dialogID', None)
        message  = data.get('message', None)

        if dialogID == None or message == None:
            return ({'status': False, 'errors': 'Не верный формат запроса'})

        answer = {'status': False}

        if validate_uuid4(dialogID):

            dialogObj = Dialog.GetCurrentDialog(dialogID)

            if dialogObj == None:
                answer['errors'] = 'Не верный идентификатор диалога'

            elif dialogObj.idUser1 == user or dialogObj.idUser2 == user:

                data = {
                            'idDialog':     dialogObj,
                            'text':         message,
                            'sender':       user,
                            'recipient':    dialogObj.idUser1 if user == dialogObj.idUser2 else dialogObj.idUser2
                        }

                try:
                    newMessage = MessageExpo.objects.create_message(data)

                    answer['status'] = True
                    answer['message'] = {'id': str(newMessage.id), 'created': newMessage.created.strftime("%d.%m.%Y %H:%M"), 'text': newMessage.text}
                except Exception as e:
                    answer['errors'] = 'Не удалось сохранить сообщение'

            else:

                answer['errors'] = 'Доступ запрещен'

        else:
            answer['errors'] = 'Не верный идентификатор диалога'

        return answer

    def saveComment(Comment):

        recipient   = UserType.GetUserFromWorker(worker=Comment.idWorker)
        dialog      = Dialog.GetDialog(Comment.idUser, recipient)

        print('Сохраняем отзыв как сообщение')

        if dialog != None:

            print('Сохраняем отзыв как сообщение-1')

            message = MessageExpo()

            message.idDialog    = dialog
            message.sender      = Comment.idUser
            message.recipient   = recipient
            message.text        = 'Добавлен отзыв: '+Comment.text+' ('+str(Comment.rating)+'зв.)'

            message.save()

    def SaveJobResponse(Jobresponse, userType):

        if userType == 1:
            user1 = UserType.GetUserFromWorker(worker=Jobresponse.worker)
            user2 = Jobresponse.jobOrder.author
            dialog = Dialog.GetDialog(user1, user2)

            if dialog != None:

                message = MessageExpo()

                message.idDialog    = dialog
                message.sender      = user1
                message.recipient   = user2
                message.subject     = 'Добавлен отклик на заявку'
                message.text        = Jobresponse.answer
                message.object      = Jobresponse.jobOrder
                message.save()

        elif userType == 2:

            user1 = UserType.GetUserFromWorker(worker=Jobresponse.worker)
            user2 = Jobresponse.jobOrder.author
            dialog = Dialog.GetDialog(user1, user2)

            if dialog != None:

                message = MessageExpo()

                message.idDialog    = dialog
                message.sender      = user2
                message.recipient   = user1
                message.subject     = 'Ответ на отклик по заказу'
                message.object      = Jobresponse.jobOrder

                if Jobresponse.status == 1:
                    message.text        = "Мы готовы сделать вам предложение"
                elif Jobresponse.status == 2:
                    message.text        = "Извините, на данный момент мы не готовы сделать вам предложение"
                else:
                    return

                message.save()

        def GetActualCount(user):

            count = 0

            if user.is_authenticated:

                count = MessageExpo.objects.all().filter(recipient=user).filter(read=False).aggregate(models.Avg('recipient'), models.Count('id')).get('id__count', 0)

            return count

    def GetActualCount(user):

        count = 0

        if user.is_authenticated:

            count = MessageExpo.objects.all().filter(recipient=user).filter(read=False).aggregate(models.Avg('recipient'), models.Count('id')).get('id__count', 0)

        return count

def professions_changed(sender, **kwargs):
    # Do something
    print("Действие с мэни ту мэни")
    if kwargs['action'] == "post_clear" or kwargs['action'] == "post_add":
        Professions.setWorkerCount(sender)

m2m_changed.connect(professions_changed, sender=Worker.professions.through)

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        print('sender: '+str(sender))
#        print('instance: ' +str(instance))
#        Worker.addWorker(user=instance, type=1)
