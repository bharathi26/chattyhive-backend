from django.conf.global_settings import LANGUAGES
from django.db import IntegrityError

__author__ = 'lorenzo'

from django.contrib import admin
from django import forms
from core.models import ChUser, ChProfile, ChHive, ChMessage, ChChat, ChSubscription, ChCategory, LanguageModel


class LanguagesAdmin(admin.ModelAdmin):
    actions = ['create_language_default_models']

    def create_language_default_models(self, request, queryset):
        for char_language in LANGUAGES:
            try:
                lang = LanguageModel(language=char_language[0])
                lang.save()
            except IntegrityError:
                continue
    create_language_default_models.short_description = "create default language models"


# Include all models in Admin site
admin.site.register(ChUser)
admin.site.register(ChProfile) #, ProfileAdmin)
admin.site.register(ChCategory)
admin.site.register(ChHive)
admin.site.register(ChMessage)
admin.site.register(ChChat)
admin.site.register(ChSubscription)
admin.site.register(LanguageModel, LanguagesAdmin)