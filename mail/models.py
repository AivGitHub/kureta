import hashlib
import pathlib

from django.db import models
import magic

_magic = magic.Magic(mime=True)


class Server(models.Model):
    server = models.CharField(
        'Server name',
        max_length=256,
        null=False,
        blank=False
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
        db_table = 'server'

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
    sender = models.CharField(
        'Sender',
        max_length=256,
        null=False,
        blank=False
    )
    recipients = models.TextField(
        'Recipients',
        null=False,
        blank=False
    )


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
