from django import template
from django.conf import settings
from datetime import datetime
from main.models import Attacment, UserType, Message
register = template.Library()


# Регистрируем тег, с помощью которого будем получать атрибуты из файла settings
@register.simple_tag
def get_attribute(name):
    return getattr(settings, name, "")

@register.filter
def create_range(value, start_index=0):
    year = datetime.now().year

    return range(1990, year+1)

@register.filter
def getresizelink(obj):

    fotourl = ''

    if obj.is_authenticated:

        userobject = UserType.GetElementByUser(obj)

        if userobject != None:
            fotourl = Attacment.getresizelink(userobject.image)

    return fotourl

@register.filter
def getname(obj):

    name = ''

    if obj.is_authenticated:

        userobject = UserType.GetElementByUser(obj)

        if userobject != None:
            name = userobject.name

    return name

@register.filter
def getactualmessage(obj):

    count = ''

    if obj.is_authenticated:

        count = Message.GetActualCount(user = obj)

        if count == 0:
            count = ''

    return count


@register.filter
def decline(value, start_index=0):

    a = (int(value) % 10)

    if int(value) == 13 or int(value) == 14:
        y = 'лет' 
    elif a == 1:
        y = 'год'
    elif a == 2 or a == 3 or a == 4:
        y = 'года'
    else:
        y = 'лет'

    return y