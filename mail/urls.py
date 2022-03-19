from django.urls import path
from django.views.generic import RedirectView

from mail.views import (
    Feed,
    PrivacyAndSafety,
    Profile,
    ProfileSettings
)


app_name = 'mail'


urlpatterns = [
    path('', RedirectView.as_view(url='feed/'), name='mail_index'),
    path('feed/', Feed.as_view(), name='feed'),
    path('profile/', Profile.as_view(), name='profile'),
    path('settings/', RedirectView.as_view(url='/mail/settings/profile/'), name='settings'),
    path('settings/profile/', ProfileSettings.as_view(), name='settings_profile'),
    path('settings/privacy_and_safety/', PrivacyAndSafety.as_view(), name='privacy_and_safety'),
]
