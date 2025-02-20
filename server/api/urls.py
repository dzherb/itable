from django.urls import include, path

from api import views

app_name = 'api'

urlpatterns = [
    path(
        'auth/',
        include(
            [
                path('login/', views.auth.login, name='login'),
            ],
        ),
    ),
]
