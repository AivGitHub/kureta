from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, render, redirect
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
    UserCreationForm
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
        _registered = request.GET.get('registered', None)

        if _registered == 'true':
            self.extra_context = {'registered': 'true'}

        if request.user.is_authenticated:
            return redirect('/mail/')

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
        _id = request.user.pk

        _messages = WallMessage.objects.filter(sender_id=_id).order_by('id')
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

        return render(
            request,
            'admin/profile/profile.html',
            {
                'wall_messages': _obj,
                'user_form': user_form,
                'errors': kwargs.get('errors')
            }
        )

    def post(self, request, *args, **kwargs):
        _id = request.user.pk
        _user = get_object_or_404(User, id=_id)

        form_class = modelform_factory(User, form=UserChangeForm, fields=('avatar',))
        form = form_class(request.POST, request.FILES, instance=_user)

        if form.is_valid():
            form.save(commit=True)

            return redirect(request.META.get('HTTP_REFERER'))

        kwargs.update({'errors': form.errors})

        return self.get(request, *args, **kwargs)


class SettingsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'admin/settings/settings.html',
            {
            }
        )


class PrivacyAndSafetySettings(LoginRequiredMixin, View):
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
                'form': change_password_form
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
                'form': change_password_form
            }
        )


class WallView(View):

    def post(self, request, *args, **kwargs):
        raise Exception('posted')


class ErrorHandler404(View):

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'error_handlers/404.html',
            {
            }
        )
