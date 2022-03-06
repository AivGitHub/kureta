from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from mail.models import Message


class SignUp(View):

    def get(self, request):
        return HttpResponse('SignUp')


class SignIn(View):

    def get(self, request):
        return HttpResponse('SignIn')


class Profile(LoginRequiredMixin, View):
    login_url = '/mail/signin/'

    def get(self, request):
        _messages = Message.objects.all()
        _paginator = Paginator(_messages, 30)
        _page_number = request.GET.get('page')
        _obj = _paginator.get_page(_page_number)

        return render(
            request,
            'mail/messages.html',
            {
                'obj': _obj,
                'amount': len(_messages)
            }
        )
