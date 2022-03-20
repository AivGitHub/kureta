from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View

from mail.models import Message
from mail.forms import (
    PasswordChangeForm,
    UserCreationForm
)


class RegisterView(View):
    register_template = 'registration/register.html'

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/login/?registered=true')

        return render(request=request, template_name=self.register_template,
                      context={'form': form})

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect('/mail/')

        form = UserCreationForm()

        return render(request, self.register_template, {'form': form})


class LoginView(DjangoLoginView):

    def get(self, request, *args, **kwargs):
        _registered = request.GET.get('registered', None)

        if _registered == 'true':
            self.extra_context = {'registered': 'true'}

        if request.user.is_authenticated:
            return redirect('/mail/')

        return super().get(self, request, *args, **kwargs)


class Feed(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'profile/feed/index.html',
            {
            }
        )


class Profile(LoginRequiredMixin, View):
    login_url = '/login/'

    class Meta:
        ordering = ['id']

    def get(self, request, *args, **kwargs):
        _id = request.user.pk

        _messages = Message.objects.filter(sender_id=_id).order_by('id')
        _paginator = Paginator(_messages, 30)
        _page = request.GET.get('page')
        _obj = _paginator.get_page(_page)

        return render(
            request,
            'profile/profile.html',
            {
                'messages': _obj,
                'amount': len(_messages)
            }
        )


class ProfileSettings(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'profile/settings/profile.html',
            {
            }
        )


class PrivacyAndSafety(LoginRequiredMixin, View):
    """
    Careful: PasswordChangeForm need user in first argument.
    """
    login_url = '/login/'
    privacy_and_safety_template = 'profile/settings/privacy_and_safety.html'

    def get(self, request, *args, **kwargs):
        change_password_form = PasswordChangeForm(request.user)

        return render(
            request,
            self.privacy_and_safety_template,
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
            self.privacy_and_safety_template,
            {
                'form': change_password_form
            }
        )


class ErrorHandler404(View):

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'error_handlers/404.html',
            {
            }
        )
