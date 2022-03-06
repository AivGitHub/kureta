from django.contrib import admin

from mail.forms import ServerForm
from mail.models import Server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):

    form = ServerForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
