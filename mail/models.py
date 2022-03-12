import hashlib
import pathlib

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
import magic

from mail.managers import UserManager

_magic = magic.Magic(mime=True)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        'username',
        max_length=150,
        help_text='150 characters or fewer. Letters and digits only.',
        error_messages={
            'unique': 'A user with that username already exists.',
        },
        null=True,
        blank=True,
        unique=True
    )
    first_name = models.CharField(
        'First name',
        max_length=150,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        'Last name',
        max_length=50,
        null=True,
        blank=True
    )
    email = models.EmailField(
        'Email address',
        null=False,
        blank=False,
        unique=True
    )
    is_staff = models.BooleanField(
        'Staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'Active',
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.',
    )
    date_joined = models.DateTimeField(
        'Date joined',
        default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_server(self):
        return self.email.split('@')[1]

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'

        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Server(models.Model):
    server = models.CharField(
        'Server name',
        max_length=256,
        null=False,
        blank=False,
        unique=True
    )
    port = models.IntegerField(
        'Port',
        null=False,
        blank=False,
        default=587
    )
    ssl = models.BooleanField(
        'SSL',
        default=False
    )

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def __str__(self) -> str:
        return self.server


class Message(models.Model):
    subject = models.CharField(
        'Subject',
        max_length=512,
        null=True,
        blank=True
    )
    body = models.TextField(
        'Text body',
        null=True,
        blank=True
    )
    sender = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    recipients = models.TextField(
        'Recipients',
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self) -> str:
        return str(self.pk)


class Attachment(models.Model):
    file = models.FileField(
        upload_to='%Y/%m/%d'
    )
    path = models.CharField(
        'path',
        max_length=512,
        null=False,
        blank=False,
    )
    mime_type = models.CharField(
        'Mime type',
        max_length=128,
        null=False,
        blank=False
    )
    name = models.CharField(
        'Name',
        max_length=128,
        null=True,
        blank=True
    )
    extension = models.CharField(
        'Mime type',
        max_length=128,
        null=False,
        blank=False
    )
    md5 = models.CharField(
        'MD5',
        max_length=32,
        null=False,
        blank=False
    )
    encrypted = models.BooleanField(
        'Encrypted',
        default=False
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

    def __str__(self) -> str:
        return self.path

    def get_md5(self):
        _hash = hashlib.md5()

        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                _hash.update(chunk)

        return _hash.hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        _file = pathlib.Path(self.path)

        self.mime_type = _magic.from_file(self.path)
        self.md5 = self.get_md5()

        try:
            self.name, self.extension = _file.name.split('.')
        except ValueError:
            self.name = _file.name

        super().save()
