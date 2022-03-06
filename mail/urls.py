from django.urls import path

from mail.views import SignUp
from mail.views import SignIn
from mail.views import Profile


urlpatterns = [
    path('', Profile.as_view()),
    path('signup/', SignUp.as_view()),
    path('signin/', SignIn.as_view())
]
