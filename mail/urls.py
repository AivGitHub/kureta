from django.urls import path
from django.views.generic import RedirectView

from mail.views import (
    Feed,
    Profile
)


app_name = 'mail'


urlpatterns = [
    path('', RedirectView.as_view(url='feed/'), name='mail_index'),
    path('feed/', Feed.as_view(), name='feed'),
    path('profile/', Profile.as_view(), name='profile')
]
