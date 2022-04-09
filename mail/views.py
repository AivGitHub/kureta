from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View

from mail.models import (
    Message,
    User,
    WallMessage
)
from mail.forms import (
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
    WallMessageForm
)


class RegisterView(View):
    register_template = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/mail/')

        form = UserCreationForm()

        return render(request, self.register_template, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/login/?registered=true')

        return render(request=request, template_name=self.register_template,
                      context={'form': form})


class LoginView(DjangoLoginView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/mail/')

        _registered = request.GET.get('registered', None)

        if _registered == 'true':
            self.extra_context = {'registered': 'true'}

        return super().get(self, request, *args, **kwargs)


class FeedView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'admin/feed/feed.html',
            {
            }
        )


class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'

    class Meta:
        ordering = ['id']

    def get(self, request, *args, **kwargs):
        if not kwargs:
            _user = request.user
            _user_id = _user.pk
        else:
            try:
                _user = User.objects.get(Q(**kwargs))
                _user_id = _user.id
            except (User.DoesNotExist, FieldError):
                # TODO: Classify exceptions
                return redirect('/mail/profile/')

        _messages = WallMessage.objects.filter(recipient_id=_user_id).order_by('-id')
        _paginator = Paginator(_messages, 10)
        _page = request.GET.get('wall_page')
        _obj = _paginator.get_page(_page)

        user_form = modelform_factory(
            User,
            fields=('avatar',),
            widgets={
                'avatar': forms.FileInput(
                    attrs={
                        'class': 'd-none'
                    }
                )
            }
        )

        wall_message_form = WallMessageForm()

        return render(
            request,
            'admin/profile/profile.html',
            {
                'user': _user,
                'wall_messages': _obj,
                'user_form': user_form,
                'errors': kwargs.get('errors'),
                'wall_message_form': wall_message_form
            }
        )

    def post(self, request, *args, **kwargs):
        """
        TODO: Think why "form_name in request.POST" does not work. Remove useless hidden inputs with form name.
        """
        _form_name = request.POST.get('form_name')
        _user_sender = request.user
        _user_recipient = request.user

        if kwargs:
            try:
                _user_recipient = User.objects.get(Q(**kwargs))
            except (User.DoesNotExist, FieldError):
                # TODO: Classify exceptions
                return redirect('/mail/profile/')

        if _form_name == 'upload_form':

            if _user_recipient != _user_sender:
                return redirect('/mail/profile/')

            form_class = modelform_factory(User, form=UserChangeForm, fields=('avatar',))
            form = form_class(request.POST, request.FILES, instance=_user_sender)

            if form.is_valid():
                form.save()

                return redirect(request.META.get('HTTP_REFERER'))

            kwargs.update({'errors': form.errors})

            return self.get(request, *args, **kwargs)
        elif _form_name == 'wall_message_form':
            form = WallMessageForm(request.POST, request.FILES)

            if form.is_valid():
                form.save(request=request, **{'sender': _user_sender, 'recipient': _user_recipient})

                return redirect(request.META.get('HTTP_REFERER'))

            kwargs.update({'errors': form.errors})

            return self.get(request, *args, **kwargs)

        return redirect(request.META.get('HTTP_REFERER'))


class SettingsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'admin/settings/settings.html',
            {
            }
        )


class PrivacyAndSafetySettingsView(LoginRequiredMixin, View):
    """
    Careful: PasswordChangeForm need user in first argument.
    """
    login_url = '/login/'
    privacy_and_safety_settings_template = 'admin/settings/privacy_and_safety.html'

    def get(self, request, *args, **kwargs):
        change_password_form = PasswordChangeForm(request.user)

        return render(
            request,
            self.privacy_and_safety_settings_template,
            {
                'change_password_form': change_password_form
            }
        )

    def post(self, request, *args, **kwargs):
        change_password_form = PasswordChangeForm(request.user, request.POST)

        if change_password_form.is_valid():
            change_password_form.save()
            update_session_auth_hash(request, change_password_form.user)

        return render(
            request,
            self.privacy_and_safety_settings_template,
            {
                'change_password_form': change_password_form
            }
        )


class WallView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        raise Exception('Posted')


class CommunicationView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(request, 'admin/profile/communication.html')


class ErrorHandler404(View):

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'error_handlers/404.html',
            {
            }
        )
