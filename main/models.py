from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from django.db.models.signals import m2m_changed, post_save
from expo.DataSet import savefile
import datetime
import uuid
from django.dispatch import receiver

# СООБЩЕНИЯ-----------------------------------------------------
class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# ---------------------------------------------------------------

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
    chatRoom            = models.ManyToManyField(ChatRoom)
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


class Company(models.Model):

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name            = models.CharField(max_length=100)
    vatnumber       = models.CharField(max_length=10)
    foto            = models.ImageField(null=True, blank=True, upload_to="img/", verbose_name='Изображение')
    phonenumber     = models.CharField(max_length=100)
    emailaddress    = models.CharField(max_length=100)
    idCity          = models.ForeignKey(City, on_delete=models.CASCADE, default="00000000000000000000000000000000")

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

class Order(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date   = models.DateTimeField("Дата создания", auto_now_add=True, null=True)
    date = models.DateTimeField("Дата создания", auto_now_add=True, null=True)
    executiondate = models.DateTimeField("Дата создания", auto_now_add=True, null=True)

class Message(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Worker, related_name="Отправитель", verbose_name="Отправитель", on_delete=models.CASCADE)
    consignee = models.ForeignKey(ChatRoom, related_name="Получатель", verbose_name="Получатель", on_delete=models.CASCADE)
    text = models.TextField("Сообщение")
    created = models.DateTimeField("Дата добавления", auto_now_add=True, null=True)
    moderation = models.BooleanField("Модерация", default=False)

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


