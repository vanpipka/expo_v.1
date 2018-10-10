from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from django.db.models.signals import m2m_changed, post_save
from expo.SaveFile import savefile
import datetime
import uuid
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
    country     = models.ForeignKey(Country, on_delete=models.CASCADE)

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
    foto           = models.ImageField(null=True, blank=True, upload_to="img/", verbose_name='Изображение')
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
                        'fotourl': '/static/main/media/' + str(companyObject.foto) if companyObject.foto else '',
                        'resizefotourl': '/static/main/media/resize' + str(companyObject.foto) if companyObject.foto else '',
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

                fileurl = savefile(base64data=strOne, src='foto', resizeit=True)

                if fileurl:
                    company.foto = fileurl

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

        for e in objects:

            e['response_is_available'] = response_array.count(e['id']) == 0

        return objects

    def SaveResponse(user, data):

        userType = UserType.GetUserType(user)

        if userType == 1:

            try:

                jobOrder = JobResponse()

                jobOrder.jobOrder = JobOrder.objects.get(id=data['job_id'])
                jobOrder.worker   = UserType.GetElementByUser(user)
                jobOrder.description  = data.get('job_description', '')

                jobOrder.save()

            except:

                return False

            return True

        else:

            return False

    def SaveOrder(user, data):

        userType = UserType.GetUserType(user)

        if userType == 2:

            try:

                jobOrder = JobOrder()

                jobOrder.company        = UserType.GetElementByUser(user)
                jobOrder.description    = data.get('job_description', '')
                jobOrder.city           = City.objects.get(id=data.get('job_city', '00000000000000000000000000000000'))

                try:
                    jobOrder.date = datetime.datetime.strptime(data.get('job_date', "1960-01-01"), "%Y-%m-%d")
                except:
                     print('ошибка при сохранении даты рождения: ' + str(worker) + '/1960-01-01')


                jobOrder.save()

            except:

                return False

            return True

        else:

            return False

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

    def GetElementByUser(user):

        elem = None

        try:
            element = UserType.objects.get(user=user)

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
    idUser      = models.ForeignKey(Worker, related_name="User", verbose_name="Пользователь", on_delete=models.CASCADE)
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

    def setRating(comment):
        rating = Comments.objects.all().filter(idWorker=comment.idWorker).aggregate(models.Avg('rating'), models.Count('id'))

        WorkerRating.updateRating(comment.idWorker, rating)

        #print("Количество:" +str(commentCount)+ " среднее:" + str(rating))

    def GetActual(self, position_begin=None, position_end=None):

        objects = Comments.objects.all().select_related("Worker").filter(moderation=True).filter(rating__gte=3).order_by("-created")

        if position_begin != None and position_end != None:
            objects = objects[position_begin: position_end]

        objects = list(objects.values('idWorker_id', 'idWorker__name', 'idWorker__surname', 'idWorker__foto', 'text'))

        for e in objects:

            ratingInfo = Worker.getWorkerRating(e['idWorker_id'])
            e['rating'] = ratingInfo['rating']

        return objects

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


