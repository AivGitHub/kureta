from django.urls import path

from mail.views import Profile


urlpatterns = [
    path('profile/', Profile.as_view())
]
