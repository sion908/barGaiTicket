from django.urls import path
from .views import (
    top, howto, asct,
    Login, Logout,
    AccountRegistration)

app_name = 'accounts'

urlpatterns = [
    path("", top, name="top"),
    path("howto", howto, name="howto"),
    path("asct", asct, name="asct"),

    path('login', Login, name='login'),
    path("logout", Logout.as_view(), name="logout"),
    path('register', AccountRegistration.as_view(), name='register'),
]
