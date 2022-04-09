import hashlib
import pathlib

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import magic
from PIL import Image

import settings
from mail.managers import UserManager
from mail.utils import System

_magic = magic.Magic(mime=True)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        validators=[EmailValidator(message=_("Enter a valid username."))],
        max_length=254,
        help_text=_('150 characters or fewer. Letters and digits only.'),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
        null=False,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        _('First name'),
        max_length=150,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=50,
        null=True,
        blank=True
    )
    email = models.EmailField(
        _('Email address'),
        max_length=254,
        null=True,
        blank=True,
        unique=False
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(
        _('Date joined'),
        default=timezone.now
    )
    nick = models.CharField(
        _('username'),
        # validators=[EmailValidator(message=_("Enter a valid username."))],
        max_length=254,
        help_text=_('150 characters or fewer. Letters and digits only.'),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
        null=False,
        blank=False,
        unique=True
    )
    avatar = models.ImageField(
        upload_to=System.user_photo_path,
        null=True,
        blank=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    AVATAR_WIDTH = 250
    AVATAR_HEIGHT = 250

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar:
            _avatar_path = pathlib.Path(self.avatar.path)
            _media_root_path = pathlib.Path(settings.MEDIA_ROOT)
            _avatar_thumbnail_name = f'{_avatar_path.stem}_thumbnail{_avatar_path.suffix}'
            _avatar_thumbnail_path = _media_root_path / System.user_photo_path(self, _avatar_thumbnail_name)

            _avatar_thumbnail = Image.open(self.avatar)

            _avatar_thumbnail.thumbnail((self.AVATAR_WIDTH, self.AVATAR_HEIGHT))
            _avatar_thumbnail.save(_avatar_thumbnail_path)

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_domain(self) -> str:
        return self.username.split('@')[1]

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        if self.first_name:
            return self.first_name

        if self.last_name:
            return self.last_name

        if self.nick:
            return self.nick

        return self.username

    def get_short_name(self) -> str:
        return self.first_name

    def get_avatar_thumbnail_url(self):
        if not self.avatar:
            return pathlib.Path(settings.STATIC_ROOT) / 'img/admin/profile.png'

        _avatar_path = pathlib.Path(self.avatar.url)

        return _avatar_path.parent / f'{_avatar_path.stem}_thumbnail{_avatar_path.suffix}'

    def email_user(self, subject, message, from_email=None, **kwargs) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Server(models.Model):
    name = models.CharField(
        _('Server name'),
        max_length=256,
        null=False,
        blank=False,
        unique=True
    )
    port = models.IntegerField(
        _('Port'),
        null=False,
        blank=False,
        default=587
    )
    ssl = models.BooleanField(
        _('SSL'),
        default=False
    )

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')

    def __str__(self) -> str:
        return self.server


class Message(models.Model):
    subject = models.CharField(
        _('Subject'),
        max_length=512,
        null=True,
        blank=True
    )
    body = models.TextField(
        _('Text body'),
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipients = models.TextField(
        _('Recipients'),
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self) -> str:
        return str(self.pk)


class Attachment(models.Model):
    file = models.FileField(
        upload_to='%Y/%m/%d'
    )
    path = models.CharField(
        _('Path'),
        max_length=512,
        null=False,
        blank=False,
    )
    mime_type = models.CharField(
        _('Mime type'),
        max_length=128,
        null=False,
        blank=False
    )
    name = models.CharField(
        _('Name'),
        max_length=128,
        null=True,
        blank=True
    )
    extension = models.CharField(
        _('Mime type'),
        max_length=128,
        null=False,
        blank=False
    )
    md5 = models.CharField(
        _('MD5'),
        max_length=32,
        null=False,
        blank=False
    )
    encrypted = models.BooleanField(
        _('Encrypted'),
        default=False
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

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


class WallMessage(models.Model):
    subject = models.CharField(
        _('Subject'),
        max_length=512,
        null=True,
        blank=True
    )
    body = models.TextField(
        _('Text body'),
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wall_message_recipient'
    )
    tags = models.TextField(
        _('Tags'),
        null=True,
        blank=True
    )
    post_time = models.DateTimeField(
        _('Post time'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('Wall message')
        verbose_name_plural = _('Wall messages')

    def __str__(self) -> str:
        return str(self.pk)
