from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from main.models import Comments, Worker
from main.forms import CommentForm
from expo.DataGet import getCityList, getProfessionListWithGroup, getServiceList, gerWorkList, searchWorker
from expo.DataSet import setWorker, refreshLastOnline
from django.views.decorators.csrf import csrf_exempt
from django.middleware import csrf

# Create your views here.
def show(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    return HttpResponse('Work Settings')

def showSettings(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    if request.user.is_authenticated:
        if request.method == "POST":

            print("СОХРАНЯЕМ НАСТРОЙКИ================================================================================")
            print(request.FILES)
            print(request.POST)
            print("================================================================================")
            foto = ''
            for f in request.FILES:
                print(request.FILES.get(f))

                foto = handle_uploaded_file(request.FILES.get(f), request.user.pk)

            print(request.user.pk)

            setWorker(request.user, request.POST, foto)

            #return HttpResponse('Work Settings')
            return render(request, 'complite.html')

        else:

            worker          = gerWorkList(user_id=request.user, userAauthorized=request.user.is_authenticated)
            selectedList    = []

            if worker != None and len(worker) > 0:
                worker          = worker[0]
                selectedList    = worker.get('proflist')
            else:
                worker          = {}

            context = {'worker': worker,
                       'city': getCityList(),
                       'serviceList': getServiceList(),
                       'professionList': getProfessionListWithGroup(selectedList=selectedList)}
            print("Ответ:")
            print(worker)

            return render(request, 'WorkerSettings.html', context)
    else:
        return HttpResponse('403: Доступ запрещен')

def showSettingsJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.user.is_authenticated:

        token = csrf.get_token(request)
        print(token)

        if request.method == "POST":
            #print(request.FILES)
            #foto = ''
            #for f in request.FILES:
            #    foto = handle_uploaded_file(request.FILES.get(f), request.user.pk)

            print(request.POST)
            setWorker(request.user, request.POST)
            #return HttpResponse('Work Settings')
            context["message"] = 'success'

        else:
            worker          = gerWorkList(user_id=request.user, userAauthorized=request.user.is_authenticated)
            selectedList    = []

            if worker != None and len(worker) > 0:
                worker          = worker[0]
                selectedList    = worker.get('proflist')
            else:
                worker          = {"name": "", "surname": "", "lastname":""}

            context = {'worker': worker,
                       'city': getCityList(),
                       'serviceList': getServiceList(),
                       'professionList': getProfessionListWithGroup(selectedList=selectedList),
                       'csrfmiddlewaretoken': token}
            print("Ответ:")
            print(worker)

            #return render(request, 'WorkerSettings.html', context)
    else:
        context["message"] = '403: Доступ запрещен'

    return JsonResponse(context)

def showWorker(request):

    userAauthorized = request.user.is_authenticated

    if userAauthorized:
        refreshLastOnline(request.user)

    id = request.GET.get("id", None)

    if id == None:

        return render(request, 'SearchWorker.html', {})

    if request.method == "POST":

        form = CommentForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.idUser     = get_object_or_404(Worker, user_id=request.user)
            form.idWorker   = get_object_or_404(Worker, id=id)
            form.save()

        return redirect(showWorker)

    else:
        commentForm = CommentForm()

    workerList = gerWorkList(idWorker=[id], userAauthorized=userAauthorized)
    comments = Comments.objects.filter(idWorker=id).order_by("-created")[:10]

    print("Ответ:" + str(len(workerList)))
    return render(request, 'Worker.html', {"worker": workerList[0], "commentForm": commentForm, "comments": comments, "userAauthorized": userAauthorized})

def showWorkersJson(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    profession  = None
    id          = None

    print('Запрос: ' + str(request.POST))
    print('Куки: ' + str(request.COOKIES))

    if request.method == "GET":
        profession = request.GET.get("profession", None)
        id = request.GET.get("id", None)

        if id != None:  #пока так
            id = [id]

    context = {}
    context["dataset"] = gerWorkList(idGroup=profession, idWorker=id, userAauthorized=request.user.is_authenticated)

    return JsonResponse(context)

def showSearch(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.method == "POST":
        print('Запрос: '+str(request.POST))
        print('Тело: ' + str(request.body))
        print('Куки: '+ str(request.COOKIES))
        dictPost = dict(request.POST)
        context = searchWorker(dictPost)

    elif request.method == "GET":

        category = request.GET.get("profession", "")

        context = searchWorker(searchList={'Profession': [category]}, userAauthorized = request.user.is_authenticated)

    return render(request, 'SearchWorker.html', context)

@csrf_exempt
def my_view(request):

    if request.user.is_authenticated:
        refreshLastOnline(request.user)

    context = {}

    if request.method == "POST":
        print('Запрос: '+str(request.POST))
        print('Тело: ' + str(request.body))
        print('Куки: '+ str(request.COOKIES))
        dictPost = dict(request.POST)
        context = searchWorker(dictPost)

    elif request.method == "GET":

        category = request.GET.get("profession", "")

        context = searchWorker({'Profession': [category]})

    return render(request, 'SearchWorker.html', context)

def handle_uploaded_file(f, id):

    directory = 'C:/djangoprojects/main/static/main/media/'
    name      = 'foto/'+str(id)+'_'+f.name

    print(name)

    filename  = directory + name
    with open(filename, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)

    return name