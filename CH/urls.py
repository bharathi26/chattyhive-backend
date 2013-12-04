__author__ = 'xurxo'
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', 'chat_app.views.login_view', name='login'),
    url(r'^chat/', 'chat_app.views.chat', name='chat'),
    url(r'^logout/', 'chat_app.views.logout_view', name='logout'),
    url(r'^android.login/','chat_androidAPI.views.login', name='login'),
    url(r'^android.chat/','chat_androidAPI.views.chat', name='chat'),
    # url(r'^android.logout/', 'chat_androidAPI.views.logout', name='logout')

    url('', include('social.apps.django_app.urls', namespace='social'))
)

