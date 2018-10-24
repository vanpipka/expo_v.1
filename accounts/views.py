from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from main.models import UserType, Attacment
import json
from django.middleware import csrf

# Опять же, спасибо django за готовую форму аутентификации.
from django.contrib.auth.forms import AuthenticationForm

# Функция для установки сессионного ключа.
# По нему django будет определять, выполнил ли вход пользователь.
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout

def signup_change(request):
    return render(request, 'accounts/signup_change.html')

def signup_worker(request):
    return signup(request, type=1)

def signup_company(request):
    return signup(request, type=2)

def signup(request, type):

    signup_url = 'accounts/signup.html'

    if request.user.is_authenticated:

        if request.is_ajax():

            error_dict = {'username': 'user is authenticated'}

            return HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': error_dict}),
                                status=200,
                                content_type='application/json')

        else:
            return HttpResponseRedirect('/')

    elif request.method == 'GET':

        if request.is_ajax():

            csrfmiddlewaretoken = csrf.get_token(request)
            ajax_response = {'Access-Control-Allow-Origin': "*",
                            'csrfmiddlewaretoken': csrfmiddlewaretoken}

            ajax_response['coocies'] = {'csrftoken': request.META["CSRF_COOKIE"],
                                        'sessionid': request.session.session_key}

            return HttpResponse(json.dumps(ajax_response),
                                status=200,
                                content_type='application/json')

        else:

            return render(request, signup_url, {'form': UserCreationForm()})

    elif request.method == 'POST':

        #Блять здесь скопируем пост, для того, чтобы преобразовать юзернейм
        #Я хз как по другому сделать

        username = request.POST['username']

        post_copy = request.POST.copy()

        username = username.replace(' ', '')
        username = username.replace(')', '')
        username = username.replace('(', '')
        username = username.replace('-', '')
        username = username.replace('+7', '8')

        if username.isdigit() != True:

            error_dict = {'username': 'Номер телефона указан неверно'}

            if request.is_ajax():

                return HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': error_dict}),
                                    status=200,
                                    content_type='application/json')

            else:
                return render(request, signup_url,
                              {'username': username, 'errors': error_dict})

        else:
            post_copy['username'] = username

            form = UserCreationForm(post_copy)

            print("form_data" +str(form.data))

            # print(form.username.errors)

            username = form.data.get('username', '')
            password = form.data.get('password1', '')

            print(username)

            if form.is_valid():

                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')

                confirmphone = request.POST.get('confirmphone', [])

                if len(confirmphone) == 0:

                    if request.is_ajax():

                        response = HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': True, 'errors': {'confirmphone': 'Заполни confirmphone'}}),
                                                status=200,
                                                content_type='application/json')

                        return response

                    else:

                        return render(request, signup_url, {'form': form, 'username': username, 'password1': password, 'password2': password, 'confirmphone': True})

                else:

                    print("confirmphone = "+str(confirmphone))

                    if confirmphone == '56503':

                        form.save()

                        user = authenticate(username=username, password=password)

                        UserType.SetUserType(user=user, type=type)

                        auth_login(request, user)

                        if request.is_ajax():

                            return HttpResponse(json.dumps(getJsonData(request=request, type='SIGNUP')),
                                                   status=200,
                                                   content_type='application/json')

                        else:

                            return HttpResponseRedirect('/worker/settings/')



                    else:

                        error_dict = {'confirmphone': 'Код подтверждения указан неверно'}

                        if request.is_ajax():

                            response = HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': False,
                                                                'errors': error_dict}),
                                                    status=200,
                                                    content_type='application/json')

                            return response

                        else:

                            form.add_error(None, "Код подтверждения указан неверно")

                            return render(request, signup_url,
                                          {'form': form, 'username': username, 'password1': password, 'password2': password,
                                           'confirmphone': True, 'errors': error_dict})

            else:

                #print(form.username.errors)

                username = form.data.get('username', '')
                password = form.data.get('password1', '')

                print(username)

                error_dict = {}
                for key, value in form.errors.as_data().items():
                    error_dict[key] = str(value[0].message)

                if request.is_ajax():

                    return HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': error_dict}),
                                            status=200,
                                            content_type='application/json')

                else:
                    return render(request, signup_url, {'form': form, 'username': username, 'password1': password, 'errors': error_dict})

    else:
        return HttpResponseRedirect('/')

def Login(request):

    #if request.is_ajax():

    #    form_class = LoginFormView

    #    rendered_form_class = form_class.as_view()(request)

    #    response = HttpResponse(json.dumps(getJsonData(request=request, type='LOGIN')),
    #                        status=200,
    #                        content_type='application/json')

    #    return response

    #else:

        login_url = 'accounts/login.html'

        if request.method == 'GET':

            if request.user.is_authenticated:

                print(request.COOKIES)
                if request.is_ajax():

                    error_dict = {'username': 'user is authenticated'}

                    return HttpResponse(
                        json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': error_dict, 'requestdata':{'cookies': request.COOKIES, 'request': list(request.GET), 'body': list(request.body)}}),
                        status=200,
                        content_type='application/json')

                else:
                    return HttpResponseRedirect('/')

            elif request.is_ajax():

                print(request.COOKIES)

                csrfmiddlewaretoken = csrf.get_token(request)
                ajax_response = {'Access-Control-Allow-Origin': "*",
                                 'csrfmiddlewaretoken': csrfmiddlewaretoken,
                                 'requestdata': {'cookies': request.COOKIES, 'request': list(request.GET),
                                                 'body': list(request.body)}}

                ajax_response['coocies'] = {'csrftoken': request.META["CSRF_COOKIE"],
                                            'sessionid': request.session.session_key}

                return HttpResponse(json.dumps(ajax_response),
                                    status=200,
                                    content_type='application/json')

            else:

                return render(request, login_url, {'form': AuthenticationForm()})

        elif request.method == 'POST':

            # Блять здесь скопируем пост, для того, чтобы преобразовать юзернейм
            # Я хз как по другому сделать
            print(request.POST)
            username = request.POST['username']

            post_copy = request.POST.copy()

            username = username.replace(' ', '')
            username = username.replace(')', '')
            username = username.replace('(', '')
            username = username.replace('-', '')
            username = username.replace('+7', '8')

            print(username)

            post_copy['username'] = username
            form = AuthenticationForm(request, data=post_copy)

            if form.is_valid():

                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                # Выполняем аутентификацию пользователя.
                user = authenticate(username=username, password=password)

                if user is not None:

                    if user.is_active:

                        auth_login(request, user)

                        if request.is_ajax():

                            return HttpResponse(json.dumps(getJsonData(request=request, type='LOGIN')),
                                                    status=200,
                                                    content_type='application/json')

                        else:

                            return HttpResponseRedirect('/')

                    else:

                        if request.is_ajax():

                            return HttpResponse(json.dumps(getJsonData(request=request, type='LOGIN')),
                                                    status=200,
                                                    content_type='application/json')

                        else:

                            return HttpResponseRedirect('/')

            else:

                username = form.data.get('username', '')

                if request.is_ajax():

                    error_dict = {}

                    for key, value in form.errors.as_data().items():
                        error_dict[key] = str(value[0].message)

                    return HttpResponse(json.dumps({'Access-Control-Allow-Origin': "*", 'status': False, 'errors': error_dict}),
                                        status=200,
                                        content_type='application/json')

                else:

                    error_dict = []

                    for key, value in form.errors.as_data().items():
                        error_dict.append(str(value[0].message))

                    return render(request, login_url,
                                  {'form': form, 'username': username, 'errors': error_dict})

        else:

            if request.is_ajax():
                return HttpResponse(json.dumps(getJsonData(request=request, type='LOGIN')),
                                    status=200,
                                    content_type='application/json')
            else:
                return HttpResponseRedirect('/')

def Logout(request):

    form_class  = LogoutView

    rendered_form_class = form_class.as_view()(request)

    if request.is_ajax():

        print('LOGOUT')

        response = HttpResponse(json.dumps(getJsonData(request=request, type='LOGOUT')),
                            status=200,
                            content_type='application/json')

        return response

    else:

        #rendered_form_class

        return rendered_form_class

class LogoutView(View):

    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        auth_logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")

def getJsonData(request, type):

    ajax_response = {'Access-Control-Allow-Origin': "*"}

    csrfmiddlewaretoken = csrf.get_token(request)

    ajax_response['coocies'] = {'csrftoken': request.META["CSRF_COOKIE"],
                                'sessionid': request.session.session_key}

    if request.method == 'GET':
        ajax_response['csrfmiddlewaretoken'] = csrfmiddlewaretoken
    else:
        ajax_response['csrfmiddlewaretoken'] = request.POST.__getitem__('csrfmiddlewaretoken')

    if type == 'LOGOUT':

        if request.session.session_key == None:
            ajax_response['status'] = True
        else:
            ajax_response['status'] = False

    else:

        if request.session.session_key != None:

            userType    = UserType.GetUserType(request.user)
            elem        = UserType.GetElementByUser(request.user)

            if userType == 1:
                data = {'name': elem.name, 'surname': elem.surname, 'fotourl': Attacment.getresizelink(elem.image), 'id': str(elem.id)}

            elif userType == 2:
                data = {'name': elem.name, 'surname': '', 'fotourl': Attacment.getresizelink(elem.image), 'id': str(elem.id)}

            else:
                data = {'name': '', 'surname': '', 'fotourl': '', 'id': ''}

            ajax_response['status'] = True
            ajax_response['user'] = data

        else:
            ajax_response['status'] = False

    print(ajax_response)

    return ajax_response