from django import forms
from django.db.utils import ProgrammingError
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.core.exceptions import ValidationError

from mail.models import (Server, User)
import settings


class UserCreationForm(DjangoUserCreationForm):
    SERVER_CHOICES = (
        (f'{settings.PROJECT_NAME}.com', f'{settings.PROJECT_NAME}.com'),
    )

    try:
        # Hack for migrations
        __servers = Server.objects.all()

        if len(__servers):
            SERVER_CHOICES = ((val, val) for val in __servers)
    except ProgrammingError:
        pass

    ALLOWED_SERVERS = [__choice[0] for __choice in SERVER_CHOICES]

    first_name = forms.CharField(
        max_length=30,
        required=False
    )
    last_name = forms.CharField(
        max_length=30,
        required=False
    )
    server = forms.ChoiceField(
        label='Server',
        choices=SERVER_CHOICES
    )
    username = forms.CharField(
        help_text='50 characters or fewer. Low letters only. '
                  'If you leave empty, than username will be default value: email without @server',
        required=False
    )

    class Meta:
        model = User
        fields = ('email', 'server', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'email': forms.TextInput(),
        }

    def clean_email(self):
        _email = self.cleaned_data.get('email')
        _email_server = _email.split('@')[1]

        if _email_server not in self.ALLOWED_SERVERS:
            raise ValidationError(
                f'Server should be of the: `{", ".join(self.ALLOWED_SERVERS)}`. Not `{_email_server}`.')

        return _email

    def clean_username(self):
        _username = self.cleaned_data.get('username')

        if not _username:
            return _username

        if not _username.isalpha():
            raise ValidationError('Username can be letters only.')

        if not _username.islower():
            raise ValidationError('Username can be lower only.')

        if _username and len(_username.split()) != 1:
            raise ValidationError('Username can\'t contain empty symbols.')

        return _username

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        _email = self.cleaned_data.get('email')
        _username = self.cleaned_data.get('username')

        if not _username.strip():
            _username = _email.split('@')[0]

        user.username = _username

        if commit:
            user.save()

        return user


class UserChangeForm(DjangoUserChangeForm):

    class Meta:
        model = User
        fields = ('email',)


class ServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = '__all__'
