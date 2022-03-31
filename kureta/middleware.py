from uuid import uuid4

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

import settings


class KuretaMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        # TODO: Log exception

        if not settings.DEBUG:
            raise exception
        else:
            return render(request, 'error_handlers/500.html', {'error_token': uuid4()})
