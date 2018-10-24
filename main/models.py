from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from django.db.models.signals import m2m_changed #, post_save
import datetime
import uuid
import base64
from PIL import Image
from django.conf import settings
from os import path

from django.dispatch import receiver

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

        if base64data.find('base64') == -1:
            return ''
        if base64data.find('image/') == -1:
            return ''

        d = base64data.partition(",")
        print("Фото======================================================================")

        strOne = d[2]
        strOne = strOne.encode()
        strOne = b"=" + strOne

        your_media_root = settings.MEDIA_ROOT
        directory = str(your_media_root)

        name = str(uuid.uuid4()) + '.png'

        #
        fullpath = path.join(directory, src, name)

        attachment = Attacment()

        print(fullpath)

        try:
            with open(fullpath, "wb") as fh:
                fh.write(base64.decodebytes(strOne.strip()))

                attachment.path = fullpath.replace(directory, '').replace('\\', '/')

            if resizeit:
                resizename = str(uuid.uuid4()) + '.png'
                fullresizepath = path.join(directory, 'attacmentresize', resizename)

                Attacment.scale_image(input_image_path=fullpath, output_image_path=fullresizepath)
                attachment.resizePath = fullresizepath.replace(directory, '').replace('\\', '/')

        except:
            attachment.path = ''
            attachment.resizePath = ''

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
            return str(settings.MEDIA_URL) + str(attach.resizePath)
        else:
            return str(settings.STATIC_URL) + 'main/img/add-photo.png'

    def getlink(attach):
        if attach.path:
            return str(settings.MEDIA_URL) + str(attach.path)
        else:
            return str(settings.STATIC_URL) + 'main/img/add-photo.png'

class Worker(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    #user_id     = models.OneToOneField(User, on_delete=models.CASCADE)
    #user_id     = models.IntegerField()
    name        = models.CharField(max_length=100)
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
    WorkerAttachment    = models.ManyToManyField(WorkerAttachment)
    salary              = models.DecimalField(max_digits=10, decimal_places=0, default=0) #Цена основной работы

    def __str__(self):
        return self.name

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

class Company(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name            = models.CharField(max_length=100)
    vatnumber       = models.CharField(max_length=10)
    foto            = models.ImageField(null=True, blank=True, upload_to="img/", verbose_name='Изображение')
    image           = models.ForeignKey(Attacment, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    phonenumber     = models.CharField(max_length=100)
    emailaddress    = models.CharField(max_length=100)
    description     = models.TextField()
    idCity          = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")

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

class News(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    description = models.TextField()
    created     = models.DateTimeField("Дата добавления", auto_now_add=True)
    link        = models.CharField(max_length=100)
    image       = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def GetActual(self, position_begin=None, position_end=None):

        objects = News.objects.all().order_by("-created")

        if position_begin != None and position_end != None:
            objects = objects[position_begin: position_end]

        objects = list(objects.values('id', 'name', 'description', 'link', 'image', 'created'))

        for e in objects:

            if e['image']:
                e['image'] = str(settings.MEDIA_URL) + str(e['image'])

        return objects

class JobOrder(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    created     = models.DateTimeField("Дата добавления", auto_now_add=True)
    date        = models.DateTimeField("Дата проведения работ", default=datetime.date(1900, 1, 1))
    place       = models.CharField(max_length=100)
    company     = models.ForeignKey(Company, on_delete=models.CASCADE)
    city            = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")
    responseCount   = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    deleted         = models.BooleanField(default=False)

    def __str__(self):
        return self.description

    def GetActual(self, user=None):

        response_array = []

        if User != None:

            userType = UserType.GetUserType(user)

            if userType == 1:

                worker = UserType.GetElementByUser(user)

                response_list = list(JobResponse.objects.filter(worker=worker).values('jobOrder_id'))

                for e in response_list:
                    if response_array.count(e['jobOrder_id']) == 0:
                        response_array.append(e['jobOrder_id'])

        objects = list(JobOrder.objects.all().select_related('city').select_related('company').order_by("-created").values('id', 'responseCount', 'description', 'date', 'place', 'created', 'company', 'city', 'city_id', 'city__name', 'company__name'))

        id_jobs = []

        for e in objects:
            id_jobs.append(e['id'])

        #print(id_jobs)

        jobComposition = list(JobComposition.objects.all().filter(jobOrder_id__in=id_jobs).select_related('profession').values('jobOrder_id', 'profession__id', 'profession__name', 'count', 'price'))

        print(jobComposition)

        for e in objects:

            e['response_is_available'] = response_array.count(e['id']) == 0

            e['job_composition'] = []

            for j in jobComposition:
                if j['jobOrder_id'] == e['id']:
                    e['job_composition'].append(j)



        return objects

    def SaveResponse(user, data):

        userType = UserType.GetUserType(user)

        if userType == 1:

            try:

                jobResponse = JobResponse()

                jobResponse.jobOrder = JobOrder.objects.get(id=data['job_id'])
                jobResponse.worker   = UserType.GetElementByUser(user)
                jobResponse.description  = data.get('job_description', '')

                jobResponse.save()

            except:

                return False

            return True

        else:

            return False

    def SaveOrder(user, data):

        userType = UserType.GetUserType(user)

        if userType == 2:

            #try:

                jobOrder = JobOrder()

                jobOrder.company        = UserType.GetElementByUser(user)
                jobOrder.description    = data.get('job_description', '')
                jobOrder.city           = City.objects.get(id=data.get('job_city', '00000000000000000000000000000000'))

                try:
                    jobOrder.date = datetime.datetime.strptime(data.get('job_date', "1960-01-01"), "%Y-%m-%d")
                except:
                     print('ошибка при сохранении даты рождения: ' + str(jobOrder) + '/1960-01-01')


                jobOrder.save()

                job_composition = data.get('job_composition', [])

                for e in job_composition:

                    if e.get('id', ''):

                        Composition = JobComposition()

                        Composition.jobOrder = jobOrder
                        Composition.profession = Professions.objects.get(id=e.get('id', ''))
                        Composition.count = int(e.get('count', 0))
                        Composition.price = int(e.get('price', 0))

                        Composition.save()

            #except:

                return False

            #return True

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
    status   = models.DecimalField(max_digits=2, decimal_places=0, default=0)

    def save(self, *args, **kwargs):
        super(JobResponse, self).save(*args, **kwargs)  # Call the "real" save() method.

        self.jobOrder.responseCount = len(JobResponse.objects.filter(jobOrder = self.jobOrder).values('id'))
        self.jobOrder.save()

        Message.SaveJobResponse(self)

class UserType(models.Model):

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    type    = models.DecimalField(max_digits=2, decimal_places=0)
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
                userType.worker = worker
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

            print(element)

            if element.type == 1:
                elem = element.worker
            else:
                elem = element.company

        except ObjectDoesNotExist:
            print('не удалось получить запись userType')

        return elem

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
        Message.SaveComment(self)

    def setRating(comment):
        rating = Comments.objects.all().filter(idWorker=comment.idWorker).aggregate(models.Avg('rating'), models.Count('id'))

        WorkerRating.updateRating(comment.idWorker, rating)

        #print("Количество:" +str(commentCount)+ " среднее:" + str(rating))

    def GetActual(self, position_begin=None, position_end=None):

        objects = Comments.objects.all().select_related("Worker").filter(moderation=True).filter(rating__gte=3).order_by("-created")

        if position_begin != None and position_end != None:
            objects = objects[position_begin: position_end]

        objects = list(objects.values('idWorker_id', 'idWorker__name', 'idWorker__surname', 'idWorker__image', 'text'))

        for e in objects:

            ratingInfo = Worker.getWorkerRating(e['idWorker_id'])
            e['rating'] = ratingInfo['rating']

            e['idWorker__image'] = Attacment.getresizelink(Attacment.objects.get(id = e['idWorker__image']))

        return objects

class Message(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender          = models.ForeignKey(User, related_name= "Отправитель", verbose_name="Отправитель", on_delete=models.CASCADE)
    recipient       = models.ForeignKey(User, related_name= "Получатель", verbose_name="Получатель", on_delete=models.CASCADE)
    text            = models.TextField("Текст")
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

    def SaveComment(Comment):

        recipient = UserType.GetUserFromWorker(worker=Comment.idWorker)

        if recipient != None:

            message = Message()

            message.sender      = Comment.idUser
            message.recipient   = recipient
            message.text        = 'Добавлен новый отзыв'
            message.comment     = Comment

            message.save()

    def SaveJobResponse(Jobresponse):

        sender = UserType.GetUserFromWorker(worker=Jobresponse.worker)

        if sender != None:

            message = Message()

            message.sender      = sender
            message.recipient   = UserType.GetUserFromCompany(company=Jobresponse.jobOrder.company)
            message.text        = 'Добавлен новый отклик на заказ'
            message.jobresponse = Jobresponse

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

        workerRating.rating         = rating['rating__avg']
        workerRating.commentsCount  = rating['id__count']

        workerRating.save()

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


