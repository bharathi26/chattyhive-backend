# -*- encoding: utf-8 -*-
from uuid import uuid4
from django.utils.translation import ugettext_lazy as _
import re
from django.core import validators
from django.utils import timezone
from colorful.fields import RGBColorField

__author__ = 'lorenzo'

from django.contrib.auth.models import AbstractUser, UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models, IntegrityError
from django import forms
from django.utils.http import urlquote
from django.conf.global_settings import LANGUAGES
from django.core.validators import RegexValidator
from email_confirmation.models import EmailAddress, EmailAddressManager, EmailConfirmation, EmailConfirmationManager
import hashlib


class ChUserManager(UserManager):
    # Creates a simple user with only email and password
    def create_user(self, username, email, password, *args, **kwargs):
        """
        :param username: Email of the user used as username
        :param email: Email also saved
        :param password: Password for the user
        :param args:
        :param kwargs:
        :return: Normal user
        """
        hex_username = '0084dcf6ba8e49278d7b00e7349146' #uuid4().hex[:30]     # 16^30 values low collision probabilities
        user = ChUser(username=hex_username)
        user.email = email
        user.set_password(password)

        while True:
            try:
                user.save(using=self._db)
                return user
            # if the email is already used
            except IntegrityError:
                user.username = uuid4().hex[:30]     # 16^30 values low collision probabilities

    # Creates a user with privileges (admin & staff)
    def create_superuser(self, username, email, password):
        """
        :param username: Email
        :param email: Email
        :param password: Password
        :return: User with privileges
        """
        user = ChUser(username=username)
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class ChUser(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    email = models.EmailField(_('email address'), unique=True, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    is_authenticated = models.BooleanField(default=False)
    objects = ChUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def is_authenticated(self):
        return AbstractUser.is_authenticated(self)

    def __str__(self):
        try:
            return '@' + ChProfile.objects.get(user=self).public_name + '[' + self.username + ']'
        except ChProfile.DoesNotExist:
            return self.username + '--NO PROFILE!'


class ChProfile(models.Model):
    # Here it's defined the relation between profiles & users
    user = models.OneToOneField(ChUser, unique=True, related_name='profile')

    # Here are the choices definitions
    SEX = (
        ('male', 'Male'),
        ('female', 'Female')
    )

    # All the fields for the model Profile
    public_name = models.CharField(max_length=30,
                                   unique=True,
                                   validators=[RegexValidator(r'^[0-9a-zA-Z_]*$',
                                                              'Only alphanumeric characters an "_" are allowed.')])
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=40)
    sex = models.CharField(max_length=10, choices=SEX, default='male')
    birth_date = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    # language is a multi value field now, related_name='languages'
    timezone = models.DateField(auto_now=True, auto_now_add=True)
    location = models.TextField(null=True, blank=True)  # todo location
    private_status = models.CharField(max_length=140, blank=True, null=True)
    public_status = models.CharField(max_length=140, blank=True, null=True)
    personal_color = RGBColorField()
    # todo image fields
    # photo = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)
    # avatar = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)

    private_show_age = models.BooleanField(default=True)
    public_show_age = models.BooleanField(default=False)
    public_show_location = models.BooleanField(default=False)
    public_show_sex = models.BooleanField(default=False)
    # email_manager = EmailAddressManager()
    # confirmed = models.BooleanField(default=False)

    # Setters for all variables
    def set_public_name(self, char_name):
        """
        :param char_name: Public name of the Profile
        :return: None
        """
        self.public_name = char_name

    def set_first_name(self, char_name):
        """
        :param char_name: First name of the Profile
        :return: None
        """
        self.first_name = char_name

    def set_last_name(self, char_name):
        """
        :param char_name: Last name of the Profile
        :return: None
        """
        self.last_name = char_name

    def set_sex(self, char_sex):
        """
        :param char_sex: Sex of the Profile
        :return: None
        """
        self.sex = char_sex

    def set_birth_date(self, char_birth_date):
        """
        :param char_sex: Sex of the Profile
        :return: None
        """
        self.birth_date = char_birth_date

    def add_language(self, char_language):
        """
        :param char_language: Language of the Profile
        :return: None
        """
        language = LanguageModel(profile=self, language=char_language)
        language.save()

    def remove_language(self, char_language):
        """
        :param char_language: Language of the Profile
        :return: None
        """
        language = LanguageModel.objects.get(profile=self, language=char_language)
        language.delete()

    def set_location(self, text_location):
        """
        :param text_location: Location of the Profile
        :return: None
        """
        self.location = text_location

    def set_private_status(self, text_private_status):
        """
        :param text_location: Location of the Profile
        :return: None
        """
        self.private_status = text_private_status

    def set_public_status(self, text_public_status):
        """
        :param text_location: Location of the Profile
        :return: None
        """
        self.public_status = text_public_status

    def set_private_show_age(self, boolean_show):
        """
        :param boolean_show: Permission of showing privately the age of the Profile
        :return: None
        """
        self.private_show_age = boolean_show

    def set_public_show_age(self, boolean_show):
        """
        :param boolean_show: Permission of showing publicly the age of the Profile
        :return: None
        """
        self.public_show_age = boolean_show

    def set_show_location(self, boolean_show):
        """
        :param boolean_show: Permission of showing the location of the Profile
        :return: None
        """
        self.public_show_location = boolean_show

    def toJSON(self):
        return u'{"public_name": "%s", "first_name": "%s", "last_name": "%s", "sex": "%s",' \
               u' "timezone": "%s","location": "%s", "private_show_age": "%s", "public_show_age": "%s",' \
               u' "show_location": "%s"}'\
               % (self.public_name, self.first_name, self.last_name, self.sex, self.timezone,
                  self.location, self.private_show_age, self.public_show_age, self.show_location)

    def __str__(self):
        return '@' + self.public_name + ', Personal profile'


class LanguageModel(models.Model):
    profile = models.ForeignKey(ChProfile, related_name='languages')
    language = models.CharField(max_length=5, choices=LANGUAGES, default='es-es')

    def __str__(self):
        return self.language + ' from ' + self.profile.public_name


class ChCategory(models.Model):
    # Groups definitions
    GROUPS = (
        ('Aficiones y ocio', 'Aficiones y ocio'),
        ('Amor y amistad', 'Amor y amistad'),
        ('Arte y eventos culturales', 'Arte y eventos culturales'),
        ('Ciencias naturales', 'Ciencias naturales'),
        ('Ciencias sociales', 'Ciencias sociales'),
        ('Cine y TV', 'Cine y TV'),
        ('Compras y mercadillo', 'Compras y mercadillo'),
        ('Conocer gente', 'Conocer gente'),
        ('Deporte', 'Deporte'),
        ('Educación', 'Educación'),
        ('Estilo de vida', 'Estilo de vida'),
        ('Familia y hogar', 'Familia y hogar'),
        ('Internet', 'Internet'),
        ('Libros y cómics', 'Libros y cómics'),
        ('Motor', 'Motor'),
        ('Música', 'Música'),
        ('Noticias y actualidad', 'Noticias y actualidad'),
        ('Política y activismo', 'Política y activismo'),
        ('Salud y fitness', 'Salud y fitness'),
        ('Sitios, empresas y marcas', 'Sitios, empresas y marcas'),
        ('Tecnología e informática', 'Tecnología e informática'),
        ('Trabajo y negocios', 'Trabajo y negocios'),
        ('Viajes y turismo', 'Viajes y turismo'),
        ('Videojuegos', 'Videojuegos'),
    )

    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=140)
    group = models.CharField(max_length=32, choices=GROUPS)

    def __str__(self):
        return self.group + ': ' + self.name


class ChHive(models.Model):
    # Attributes of the Hive
    name = models.CharField(max_length=60, unique=True)
    name_url = models.CharField(max_length=60, unique=True)
    description = models.TextField()
    category = models.ForeignKey(ChCategory)
    creator = models.ForeignKey(ChProfile, null=True)  # on_delete=models.SET_NULL, we will allow deleting profiles?
    creation_date = models.DateField(auto_now=True)

    def toJSON(self):
        return u'{"name": "%s", "name_url": "%s", "description": "%s", "category": "%s", "creation_date": "%s"}' \
               % (self.name, self.name_url, self.description, self.category, self.creation_date)

    def set_creator(self, profile):
        """
        :param profile: Creator of this hive
        :return: None
        """
        self.creator = profile

    def __str__(self):
        return self.name


class ChChat(models.Model):
    # Chat TYPE definitions
    TYPE = (
        ('public', 'public'),
        ('private', 'private'),
    )

    # Relation between chat and hive
    type = models.CharField(max_length=32, choices=TYPE, default='private')
    hive = models.ForeignKey(ChHive, related_name="hive", null=True, blank=True)
    channel_unicode = models.CharField(max_length=60, unique=True)

    # Attributes of the Chat
    date = models.DateTimeField(auto_now=True)

    def set_hive(self, hive):
        """
        :param hive: Owner hive of this chat
        :return: None
        """
        self.hive = hive
        return

    def set_channel(self, channel_unicode):
        """
        :param channel_unicode: Pusher id for this chat
        :return: None
        """
        self.channel_unicode = 'presence-' + channel_unicode
        return

    def set_type(self, type):
        """
        :param channel_unicode: Pusher id for this chat
        :return: None
        """
        self.type = type
        return

    def join(self, profile):
        """
        :param profile: Object profile who wants to join to this chat
        :return: None, but will create a subscription for this relation
        """
        subscription = ChSubscription()
        subscription.set_profile(profile)
        subscription.set_chat(self)
        subscription.save()
        return

    def __str__(self):
        return self.hive.name + '(' + self.type + ')'


class ChMessage(models.Model):
    CONTENTS = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('animation', 'Animation'),
        ('url', 'URL'),
        ('file', 'File')
    )

    # Relations of a message. It belongs to a hive and to a profile at the same time
    profile = models.ForeignKey(ChProfile)
    chat = models.ForeignKey(ChChat, null=True, blank=True)

    # Attributes of the message
    content_type = models.CharField(max_length=20, choices=CONTENTS)
    date = models.DateTimeField()

    # Content of the message
    content = models.TextField(max_length=2048)

    def __str__(self):
        return self.profile.public_name + " said: " + self.content


class ChAnswer(ChMessage):
    # Relation to the message.
    message = models.ForeignKey(ChMessage, related_name='response')


class ChSubscription(models.Model):
    # Subscription object which relates Profiles with Hives/Chats
    profile = models.ForeignKey(ChProfile, unique=False)
    hive = models.ForeignKey(ChHive, null=True, blank=True, related_name='hive_subscription')
    chat = models.ForeignKey(ChChat, null=True, blank=True, related_name='chat_subscription')

    def set_chat(self, chat):
        """
        :param chat: Object chat that is relating
        :return: None
        """
        self.chat = chat
        return

    def set_profile(self, profile):
        """
        :param profile: Object profile that is relating
        :return: None
        """
        self.profile = profile
        return

    def set_hive(self, hive):
        """
        :param hive: Object hive that is relating
        :return: None
        """
        self.hive = hive
        return

        # @register.simple_tag
        # def get_verbose_name(self):
        # return object._meta.verbose_name

    def __str__(self):
        return self.profile.first_name + " links with"


### ==========================================================
###                          FORMS
### ==========================================================

class CreateHiveForm(forms.ModelForm):
    class Meta:
        model = ChHive
        fields = ('name', 'category', 'description')


class MsgForm(forms.Form):
    write_your_message = forms.CharField(max_length=128)


class PrivateProfileForm(forms.Form):
    class Meta:
        model = ChProfile
        fields = ('first_name', 'surname', 'birth_date', 'language', 'sex')


### ==========================================================
###                          METHODS
### ==========================================================

def replace_unicode(string):
    string = urlquote(string)
    string = hashlib.sha1(string.encode('utf-8')).hexdigest()
    return string