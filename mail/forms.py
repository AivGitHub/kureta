from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.core.exceptions import ValidationError
from django.db.utils import ProgrammingError
from django.utils.translation import gettext_lazy as _

from mail.models import (
    Server,
    User,
    WallMessage
)
import settings


class UserCreationForm(DjangoUserCreationForm):
    DOMAIN_CHOICES = (
        (f'@{settings.PROJECT_NAME}.com', f'@{settings.PROJECT_NAME}.com'),
    )

    try:
        # Hack for migrations
        __servers = Server.objects.all()

        if len(__servers):
            DOMAIN_CHOICES = tuple((f'@{_server.name}', f'@{_server.name}') for _server in __servers)
    except ProgrammingError:
        pass

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Username')
            }
        )
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': _('First Name')
            }
        )
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Last Name')
            }
        )
    )
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('Password')
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('Password verification')
            }
        ),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )
    domain = forms.ChoiceField(
        label=_('Domain'),
        choices=DOMAIN_CHOICES,
    )

    class Meta:
        model = User
        fields = ('username', 'domain', 'password1', 'password2', 'first_name', 'last_name')
        widgets = {}

    def clean_username(self):
        """ TODO: classify input errors
        """
        _username = self.cleaned_data.get('username')
        _allowed_domains = tuple(__domain[0] for __domain in self.DOMAIN_CHOICES)

        if '@' not in _username:
            return _username

        _domain = _username.split('@')[-1]

        if _domain not in _allowed_domains:
            raise ValidationError(f'Domain should be one of the: `{", ".join(_allowed_domains)}`.')

        return _username

    def clean(self):
        _cleaned_data = super().clean()
        _username = _cleaned_data.get('username')

        if _username and '@' not in _username:
            __domain = self.cleaned_data.get('domain')

            _cleaned_data.update({'username': f'{_username}{__domain}'})

        return _cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        _username = self.cleaned_data.get('username')

        user.email = _username
        user.nick = _username.split('@')[0]

        if commit:
            user.save()

        return user


class PasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label=_('Old password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'autofocus': True,
                'placeholder': _('Old password')
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('New password')
            }
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Password confirmation'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('Password confirmation')
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'old_password', 'new_password1', 'new_password_2')


class UserChangeForm(DjangoUserChangeForm):

    class Meta:
        model = User
        fields = '__all__'


class ServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = '__all__'


class AuthenticationForm(DjangoAuthenticationForm):
    DOMAIN_CHOICES = (
        (f'@{settings.PROJECT_NAME}.com', f'@{settings.PROJECT_NAME}.com'),
    )

    try:
        # Hack for migrations
        __servers = Server.objects.all()

        if len(__servers):
            DOMAIN_CHOICES = tuple((_server.name, _server.name) for _server in __servers)
    except ProgrammingError:
        pass

    username = UsernameField(
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'placeholder': _('Email')
            }
        )
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'placeholder': _('Password')
            }
        ),
    )
    domain = forms.ChoiceField(
        label=_('Domain'),
        choices=DOMAIN_CHOICES,
    )

    def get_invalid_login_error(self):
        return ValidationError(
            _('Please enter a correct %(username)s and password.'),
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        domain = self.cleaned_data.get('domain')

        if username and '@' not in username:
            username = f'{username}{domain}'

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class WallMessageForm(forms.ModelForm):
    subject = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'cols': 20,
                'rows': 1,
                'style': 'width: 50%',
                'class': 'form-control',
                'placeholder': _('Subject'),
            }
        ),
        required=False
    )
    tags = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'cols': 20,
                'rows': 1,
                'style': 'width: 100%',
                'class': 'form-control',
                'placeholder': _('Tags'),
            }
        ),
        required=False
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'cols': 20,
                'rows': 3,
                'style': 'width: 100%',
                'class': 'form-control',
                'placeholder': _('Message')
            }
        )
    )

    class Meta:
        model = WallMessage
        fields = ('subject', 'tags', 'body')

    def save(self, commit=True, request=None, **kwargs):
        message = super().save(commit=False)

        if request:
            message.sender = kwargs.get('sender')
            message.recipient = kwargs.get('recipient')

        if commit:
            message.save()

        return message
