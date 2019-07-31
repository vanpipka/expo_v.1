
from django.shortcuts import render, redirect
from datetime import datetime as datet
from datetime import timezone
from main.models import Company, Dialog, MessageExpo, News, JobOrder, UserType, Attacment, Message, Worker, Comments, ConfirmCodes
from expo.DataSet import refreshLastOnline
from expo.DataGet import getCityListFull, getProfessionList, gerWorkList
from expo.Balance import getBalance
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json

# Create your views here.

def termsOfUse(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'TermsOfUse.html', {})

def confidential(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'confidential.html', {})

def legal(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'legal.html', {})

def privacypolicy(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'PersonalData.html', {})

def adminexpo(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.user.is_superuser:

        context = {'balance': getBalance()}

        return render(request, 'adminexpo/adminexpo.html', context)
    else:
        return render(request, 'errors/403.html', None, None, status='403')

def testtest(request):
    return render(request, 'testtest.html', {})

def sendsms(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if userAauthorized:

        phone = request.GET.get("phone", "")

        print(phone)

        if phone != "":

            ConfirmCodes.AddCode(phoneNumber=phone)#, sendMessage=True)

        return HttpResponse(settings.HOME_PAGE + 'success/', status=200)

    else:
        return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def adminexpocompanys(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.user.is_superuser:
        if request.method == "GET":

            query = Company.objects.all().filter()
            dataset = []
            for e in query:

                dataset.append({'name': e.name,
                                    'id': e.id,
                                    'block': e.block,
                                    'email': e.emailaddress,
                                    'phone': e.phonenumber,
                                    'vatnumber': e.vatnumber
                                    })

            return render(request, 'adminexpo/adminexpocompanys.html', {"dataset": dataset})
        else:

            print(request.POST)

            if request.POST.__contains__('data'):
                data = dict(json.loads(request.POST.__getitem__('data')))
                Company.SetAdminData(data)
            return HttpResponse(settings.HOME_PAGE + 'adminexpo/companys/')
    else:
        if request.method == "GET":
            return render(request, 'errors/403.html', None, None, status='403')
        else:
            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def adminexpocomments(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.user.is_superuser:
        if request.method == "GET":

            query = Comments.objects.all().filter().select_related('idUser').select_related('idWorker').select_related(
                'idProf').order_by("-created")
            dataset = []

            for e in query:
                dataset.append({'text': e.text,
                                'id': e.id,
                                'user': {'name': e.idUser.username, 'id': e.idUser.id},
                                'worker': {'name': e.idWorker.name, 'id': e.idWorker.id},
                                'rating': e.rating,
                                'profession': e.idProf.name,
                                'moderation': e.moderation
                                })

            return render(request, 'adminexpo/adminexpocomments.html', {"dataset": dataset})
        else:

            print(request.POST)

            if request.POST.__contains__('data'):
                data = dict(json.loads(request.POST.__getitem__('data')))

                Comments.SetAdminData(data)

                return HttpResponse(settings.HOME_PAGE + 'adminexpo/comments/')
    else:
        if request.method == "GET":
            return render(request, 'errors/403.html', None, None, status='403')
        else:
            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def adminexpoworkers(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.user.is_superuser:
        if request.method == "GET":
            context = {"dataset": gerWorkList(userAauthorized=True, its_superuser=request.user.is_superuser)}
            return render(request, 'adminexpo/adminexpoworkers.html', context)
        else:

            print(request.POST)

            if request.POST.__contains__('data'):
                data = dict(json.loads(request.POST.__getitem__('data')))
                Worker.SetAdminData(data)
            return HttpResponse(settings.HOME_PAGE + 'adminexpo/workers/')
    else:
        if request.method == "GET":
            return render(request, 'errors/403.html', None, None, status='403')
        else:
            return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def adminexposave(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.user.is_superuser:

        if request.method == "POST":

            if request.POST.__contains__('data'):

                print("Сохраняем настройки компании")

                data = dict(json.loads(request.POST.__getitem__('data')))

                try:

                    f = open('expo_settings/companysettings.json', 'w')

                    f.write('{"address":"'+data.get('address', '')+'", "phone": "'+data.get('phone', '')+'", "email": "'+data.get('email', '')+'"}')
                    f.close()

                    status = True

                except:
                    status = False


            else:

                status = False

            if request.is_ajax():

                return HttpResponse(
                    json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                    status=200,
                    content_type='application/json')

            else:

                if status == True:
                    return HttpResponse(settings.HOME_PAGE + 'success/')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status='403')

def forbiden(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/403.html', None, None, status='403')

def notfound(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/404.html', None, None, status='404')

def servererror(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'errors/500.html', None, None, status='500')

def success(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    context = {'return_page': request.META.get('HTTP_REFERER', settings.HOME_PAGE)}

    print(context)

    return render(request, 'errors/success.html', context, None, status='200')

def companys(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    companyList = []

    query = Company.objects.all().filter(block=False)

    for e in query:
        companyList.append({'name': e.name,
                'id': str(e.id),
                'url': '/company?id=' + str(e.id),
                'fotourl': Attacment.getlink(e.image),
                'resizefotourl': Attacment.getresizelink(e.image),
                'isonline': True if (datet.now(timezone.utc) - e.lastOnline).seconds / 60 < 5 else False,
                'lastonline': str(e.lastOnline),
                'description': e.description
               })

    if request.is_ajax():

        return HttpResponse(
            json.dumps({'Access-Control-Allow-Origin': "*", 'dataset': companyList}),
            status=200,
            content_type='application/json')

    else:

        return render(request, 'CompanyList.html', {"companyList": companyList})

def company(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    id = request.GET.get("id", None)

    if id == None:
        return render(request, 'errors/404.html', status=404)

    query = Company.objects.all().filter(block=False).filter(id=id).select_related('idCity')

    if len(query) == 0:
        return render(request, 'errors/404.html', status=404)
    else:

        for e in query:
            company = {'name': e.name,
                                'id': e.id,
                                'url': '/company?id='+str(e.id),
                                'phonenumber': e.phonenumber,
                                'email': e.emailaddress,
                                'city': e.idCity.name,
                                'fotourl': Attacment.getlink(e.image),
                                'resizefotourl': Attacment.getresizelink(e.image),
                                'isonline': True if (datet.now(timezone.utc) - e.lastOnline).seconds / 60 < 5 else False,
                                'lastonline': e.lastOnline,
                                'description': e.description
                                }

        return render(request, 'Company.html', {"worker": company, "userAauthorized": userAauthorized})

def news(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    return render(request, 'NewsList.html', {"newsList": News.GetActual(News)})

def savenews(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated and request.user.is_superuser:

        print(request.POST.__getitem__('data'))

        if request.method == "POST":

            if request.POST.__contains__('data'):

                print("Сохраняем новую новость")

                #{"name":"1","description":"3","link":"2"}
                data = dict(json.loads(request.POST.__getitem__('data')))

                status = News.SaveResponse(user = request.user, data = data)

            else:

                status = False

            if request.is_ajax():

                return HttpResponse(
                    json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                    status=200,
                    content_type='application/json')

            else:

                if status == True:
                    return HttpResponse(settings.HOME_PAGE + 'success/')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=403,
                        content_type='application/json')
            else:
                return render(request, 'errors/403.html', None, None, status=403)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)

def messagesend(request):

    print('!!!!!!!!!')

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    if request.method == 'GET':

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ['Отправка невозможна']}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)

    else:

        if userAauthorized:

            result = Message.SaveNewMessage(Content = dict(json.loads(request.POST.__getitem__('data'))), User = request.user)

            if request.is_ajax():

                if result == True:

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': True, 'errors': []}),
                        status=200,
                        content_type='application/json')

                else:

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ['не удалось сохранить сообщение']}),
                        status=500,
                        content_type='application/json')

            else:

                if result == True:

                    return HttpResponse(settings.HOME_PAGE + 'success/')

                else:

                    return HttpResponse(settings.HOME_PAGE + 'servererror/')

        else:

            if request.is_ajax():
                return HttpResponse(
                    json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                    status=403,
                    content_type='application/json')
            else:
                return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

def dialogs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        if request.method == 'GET':
            idDialog    = request.GET.get('id', '')
            idRecipient = request.GET.get('recipient', '')
            if idDialog != '':

                messageData = MessageExpo.getMessagesByDialog(request.user, idDialog)

                if request.is_ajax():

                    return JsonResponse(messageData)

                else:

                    if (messageData['status']):

                        return render(request, 'MessageList.html', {"messageData": messageData})

                    else:

                        return redirect('/forbiden')

            elif idRecipient != '':

                print('idRecipient: '+str(idRecipient))

                recipient = UserType.GetUserByID(idRecipient)
                dialog    = None

                if recipient == None:
                    if request.is_ajax():
                        return JsonResponse({'status': False, 'errors': 'не удалось определить диалог'})
                    else:
                        return redirect('/servererror')
                else:
                    dialog = Dialog.GetDialog(request.user, recipient)

                if request.is_ajax():

                    if dialog == None:
                        return JsonResponse({'status': False, 'errors': 'не удалось определить диалог'})
                    else:

                        if (request.user == d.idUser1):
                            sender = UserType.GetElementByUser(d.idUser2)
                        else:
                            sender = UserType.GetElementByUser(d.idUser1)

                        return JsonResponse({'status': True,
                                            'dialog': {'id': dialog.id, 'sender': {'name': sender.name, 'foto': Attacment.getresizelink(sender.image)},}
                                            })

                else:

                    if dialog == None:
                        return redirect('/servererror')
                    else:
                        return redirect('/dialogs/?id='+str(dialog.id))

            else:

                dialogList = Dialog.GetDialogs(request.user)

                if request.is_ajax():

                    return JsonResponse({'status': True, 'dataset': dialogList})

                else:

                    return render(request, 'DialogsList.html', {"messageList": dialogList})

        elif request.method == 'POST':

            print("Dialog POST: "+str(request.POST))

            if request.POST.__contains__('data'):

                data    = dict(json.loads(request.POST.__getitem__('data')))
                answer  = MessageExpo.addMessageToDialog(request.user, data)
                #print("Data POST: "+str(data))

                return JsonResponse(answer)

            else:

            #dialogID = request.POST.__getitem__('dialogID')
            #message  = request.POST.__getitem__('message')

            #if message == '' or message == None:
            #    return JsonResponse({'status': False, 'errors': ['Сообщение пустое']})

            #save message

                return JsonResponse({'status': False, 'errors': ['Неверный формат запроса']})

    else:

        if request.is_ajax():

            return JsonResponse({'status': False, 'errors': ['Доступ запрещен']})

        else:

            return redirect('accounts/login/')

def messages(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:

        refreshLastOnline(request.user)

        idWho = ''

        if request.POST.__contains__('data'):

            data = dict(json.loads(request.POST.__getitem__('data')))

            idWho = data.get('id')

        messagelist = Message.GetAll(request.user, idWho)

        if request.is_ajax():

            return JsonResponse({'status': True, 'dataset': messagelist})

        else:

            return render(request, 'MessageList.html', {"messageList": messagelist})

    else:

        if request.is_ajax():

            return JsonResponse({'status': False, 'errors': ['Доступ запрещен']})

        else:

            return render(request, 'errors/403.html', None, None, status='403')            #return render(request, 'errors/403.html', None, None, status='403')

def jobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)
        jobOrders = JobOrder.GetActual(JobOrder, user = request.user);
        if request.is_ajax():

            return JsonResponse({'status': True, 'dataset': jobOrders})

        else:

            return render(request, 'JobList.html', {"jobsList": jobOrders, "userType": userType})

    else:

        print('аякс запрос - ' + str(request.is_ajax))
        if request.is_ajax():

            return JsonResponse({'status': False, 'errors': ['Доступ запрещен']})

        else:

            return render(request, 'accounts/login.html')

def newjobs(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

        userType = UserType.GetUserType(request.user)

        return render(request, 'NewJob.html', {'userType': userType, 'citylist': getCityListFull(), 'professionsList': getProfessionList()})

    else:

        return render(request, 'errors/403.html', None, None, status=403)

def newmessage(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    else:

        return render(request, 'errors/403.html', None, None, status=403)

    id      = request.GET.get("id", None)
    type    = request.GET.get("type", None)

    if id == None or type == None:
        return render(request, 'errors/404.html', status=404)

    if type == '1':
        recipient = Worker.GetElement(id = id)
    elif type == '2':
        recipient = Company.GetElement(id = id)
    else:
        return render(request, 'errors/404.html', status=404)

    if recipient == None:
        return render(request, 'errors/404.html', status=404)

    userType = UserType.GetUserType(request.user)

    content = {'recipient': {'type': type,'name': recipient.name, 'id': recipient.id, 'foto': Attacment.getresizelink(recipient.image)}}

    return render(request, 'NewMessage.html', content)

def savejobs(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            print('тип юзера: ' + str(userType))

            if userType == 1:

                if request.POST.__contains__('data'):

                    print("Сохраняем отклик")

                    print(request.POST.__getitem__('data'))

                    #{"job_id": "96ca3684-c1cf-4641-b160-01124cfcdaff", "job_description": "444"}
                    data = dict(json.loads(request.POST.__getitem__('data')))

                    status = JobOrder.SaveResponse(user = request.user, data = data)

                else:

                    status = False

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                        status=200,
                        content_type='application/json')

                else:

                    if status == True:
                        return HttpResponse(settings.HOME_PAGE + 'success/')
                    else:
                        return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)

            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return render(request, 'errors/403.html', None, None, status=403)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)

def saveorder(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:

        if request.method == "POST":

            userType = UserType.GetUserType(request.user)

            if userType == 2:

                if request.POST.__contains__('data'):

                    #{"job_id": "96ca3684-c1cf-4641-b160-01124cfcdaff", "job_description": "444"}
                    data = dict(json.loads(request.POST.__getitem__('data')))

                    status = JobOrder.SaveOrder(user=request.user, data = data)

                else:

                    status = False

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': status, 'errors': ''}),
                        status=200,
                        content_type='application/json')

                else:

                    print("сохраняем заявку" + str(status))

                    if status == True:
                        return HttpResponse(settings.HOME_PAGE + 'success/')
                    else:
                        return HttpResponse(settings.HOME_PAGE + 'servererror/', status=500)
            else:

                if request.is_ajax():

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
                else:
                    return HttpResponse(settings.HOME_PAGE + 'forbiden/', status=403)

        else:
            if request.is_ajax():

                return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                        status=404,
                        content_type='application/json')
            else:
                return render(request, 'errors/404.html', None, None, status=404)
    else:

        if request.is_ajax():
            return HttpResponse(
                json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': ''}),
                status=403,
                content_type='application/json')
        else:
            return render(request, 'errors/403.html', None, None, status=403)
