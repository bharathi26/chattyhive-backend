__author__ = 'xurxo'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'CH.views.login', name='home'),
)