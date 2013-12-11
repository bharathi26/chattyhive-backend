__author__ = 'lorenzo'

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
# from core.models import *
from login.models import *
from django.contrib.auth import authenticate, login, logout


def login_view(request):
    if request.method == 'POST':
        print("if")
        form = LoginForm(request.POST)
        if form.is_valid():
            # request.session['user'] = form.cleaned_data['user']
            # request.session['active'] = True
            username = form.cleaned_data['user']
            password = form.cleaned_data['password']
            request.session.set_expiry(300)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # login(request, user)
                    if not user.is_authenticated():
                        print("nope")
                    else:
                        print("yep")
                    return HttpResponseRedirect("/chat/")
                else:
                    return HttpResponse("ERROR, inactive user")
            else:
                return HttpResponse("ERROR, incorrect password or login")
        else:
            return HttpResponse("ERROR, invalid form")
    else:
        # print("21 /b",request.session['active'])
        if 'user' in request.session and request.session['active']==True:
            print('one')
            request.session.set_expiry(300)
            return HttpResponseRedirect("/chat/")
        else:
            form = LoginForm()
            print('two')
            return render(request, "chat_app/login.html", {
                'form': form
            })