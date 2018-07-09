from django.db import models
from django.contrib.auth.models import User

import datetime
import uuid

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
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.indexName = self.name.upper()
        super(Professions, self).save(*args, **kwargs)  # Call the "real" save() method.

class City(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    indexName   = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.indexName = self.name.upper()
        super(City, self).save(*args, **kwargs)  # Call the "real" save() method.

class Service(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class WorkerAttachment(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file        = models.FileField(null=True, blank=True, upload_to="media/attach/", verbose_name='Изображение')
    Description = models.CharField(max_length=200)

class Worker(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    #user_id     = models.IntegerField()
    name        = models.CharField(max_length=100)
    surname     = models.CharField(max_length=100)
    education   = models.TextField()
    lastname    = models.CharField(max_length=100)
    haveIP      = models.BooleanField(default=False)
    haveShengen = models.BooleanField(default=False)
    haveIntPass = models.BooleanField(default=False) #ЗагранПаспорт
    haveInstrument = models.BooleanField(default=False)
    fsocheck    = models.BooleanField(default=False)
    workpermit  = models.BooleanField(default=False)
    datacheck   = models.BooleanField(default=False)
    sex         = models.BooleanField(default=True)
    Description = models.TextField()
    idCity      = models.ForeignKey(City, on_delete=models.CASCADE)
    birthday    = models.DateField(datetime.date, default=None, null=True)
    Experiencewith = models.DateField(datetime.date, null=True)
    experience     = models.TextField()
    foto           = models.ImageField(null=True, blank=True, upload_to="img/", verbose_name='Изображение')
    lastOnline     = models.DateTimeField("Последний онлайн", auto_now_add=True, null=True)
    professions    = models.ManyToManyField(Professions)
    phonenumber    = models.CharField(max_length=100)
    emailaddress   = models.CharField(max_length=100)
    WorkerAttachment = models.ManyToManyField(WorkerAttachment)

    def __str__(self):
        return self.name

class CostOfService(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idService   = models.ForeignKey(Service, on_delete=models.CASCADE)
    idWorker    = models.ForeignKey(Worker, on_delete=models.CASCADE)
    price       = models.DecimalField(max_digits=10, decimal_places=2)

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
