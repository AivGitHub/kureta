from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from mail.models import Message
from mail.forms import UserCreationForm


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
            return redirect('/mail/profile/')

        form = UserCreationForm()

        return render(request, self.register_template, {'form': form})


class LoginView(DjangoLoginView):

    def get(self, request, *args, **kwargs):
        print(request.GET)

        _registered = request.GET.get('registered', None)

        if _registered == 'true':
            self.extra_context = {'registered': 'true'}

        if request.user.is_authenticated:
            return redirect('/mail/profile/')

        return super().get(self, request, *args, **kwargs)


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
            'profile/messages.html',
            {
                'messages': _obj,
                'amount': len(_messages)
            }
        )