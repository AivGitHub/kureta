from django import forms

from mail.models import Server


class ServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = '__all__'
