from django.urls import path
from django.views.generic import RedirectView

from mail.views import (
    FeedView,
    ProfileView,
    SettingsView,
    WallView
)


app_name = 'mail'


urlpatterns = [
    path('', RedirectView.as_view(url='feed/'), name='mail_index'),
    path('feed/', FeedView.as_view(), name='feed'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/wall', WallView.as_view(), name='wall'),
    path('settings/', RedirectView.as_view(url='/mail/settings/profile/'), name='settings'),
    path('settings/profile/', SettingsView.as_view(), name='settings_profile'),
]
