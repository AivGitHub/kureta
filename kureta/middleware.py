from uuid import uuid4

from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

import settings


class KuretaMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        # TODO: Log exception

        if settings.DEBUG:
            raise exception
        else:
            return render(request, 'error_handlers/500.html', {'unique_token': uuid4()})
