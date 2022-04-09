from django.urls import path
from django.views.generic import RedirectView

from mail.views import (
    CommunicationView,
    FeedView,
    PrivacyAndSafetySettingsView,
    ProfileView,
    SettingsView,
    WallView
)


app_name = 'mail'


urlpatterns = [
    path('', RedirectView.as_view(url='feed/'), name='mail_index'),
    path('feed/', FeedView.as_view(), name='feed'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<int:id>/', ProfileView.as_view(), name='profile_int'),
    path('profile/<str:nick>/', ProfileView.as_view(), name='profile_str'),
    path('profile/wall/', WallView.as_view(), name='wall'),
    path('communication/', CommunicationView.as_view(), name='communication'),
    path('settings/', RedirectView.as_view(url='/mail/settings/profile/'), name='settings'),
    path('settings/profile/', SettingsView.as_view(), name='settings_profile'),
    path('settings/privacy_and_safety/', PrivacyAndSafetySettingsView.as_view(), name='privacy_and_safety'),
]
