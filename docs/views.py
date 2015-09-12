# -*- encoding: utf-8 -*-
__author__ = 'xurxo'

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from core.models import *
from django.contrib.auth.decorators import login_required
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from core.pusher_extensions import ChPusher
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from docs.forms import LoginForm


@csrf_exempt
def welcome_screen(request):
    if request.method == 'GET':
        return render(request, 'docs/welcome_screen.html')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                login_string = form.cleaned_data['login']
                password = form.cleaned_data['password']
                if '@' in login_string:
                    user = ChUser.objects.get(email=login_string)
                    user = authenticate(username=user.username, password=password)
                else:
                    profile = ChProfile.objects.select_related().get(public_name=login_string)
                    # TODO: no tengo muy claro que este profile.username (se está accediendo a un campo del ChUser a
                    # través del ChProfile) esté funcionando. Ver bien lo de select_related()...
                    user = authenticate(username=profile.username, password=password)

                if not user.is_staff:
                    return HttpResponse("Sorry, only authorized developers can access to the API section")

                if user.is_active:
                    # With login we persist the authentication, so the client won't have to reathenticate with each
                    # request.
                    login(request, user)
                    return HttpResponseRedirect("/docs/project_summary")
                else:
                    return HttpResponse("Sorry, your account is not enabled")
            except ChUser.DoesNotExist or ChProfile.DoesNotExist:
                return HttpResponse("ERROR, incorrect password or login")


@csrf_exempt
@user_passes_test(lambda u:u.is_staff, login_url='/')  # This only allow stuff members to see this views
def project_summary(request):
    if request.method == 'GET':
        return render(request, 'docs/project_summary.html')


@csrf_exempt
@user_passes_test(lambda u:u.is_staff, login_url='/')  # This only allow stuff members to see this views
def api_methods(request):
    if request.method == 'GET':
        return render(request, 'docs/api_methods.html')
