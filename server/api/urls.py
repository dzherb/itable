from django.urls import include, path

from api import views

app_name = 'api'

urlpatterns = [
    path(
        'auth/',
        include(
            [
                path('login/', views.auth.login, name='login'),
                path('logout/', views.auth.logout, name='logout'),
            ],
        ),
    ),
    path('portfolios/', views.portfolios.portfolio_list, name='portfolios'),
    path(
        'portfolios/<int:pk>/',
        views.portfolios.portfolio_dispatcher.as_view(),
        name='portfolio',
    ),
    path('securities/', views.securities.security_list, name='securities'),
]
