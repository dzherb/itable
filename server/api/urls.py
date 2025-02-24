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
    path(
        'portfolios/',
        include(
            [
                path('', views.portfolios.dispatcher, name='portfolios'),
                path(
                    '<int:pk>/',
                    views.portfolios.detail_dispatcher,
                    name='portfolio',
                ),
                path(
                    '<int:portfolio_id>/securities/',
                    views.portfolios.securities.add_portfolio_security,
                    name='portfolio_securities',
                ),
                path(
                    '<int:portfolio_id>/securities/<str:security_ticker>/',
                    views.portfolios.securities.dispatcher,
                    name='portfolio_security',
                ),
            ],
        ),
    ),
    path('securities/', views.securities.security_list, name='securities'),
    path(
        'tables/',
        include(
            [
                path(
                    'snapshots/',
                    views.tables.snapshots.dispatcher,
                    name='table_snapshots',
                ),
            ],
        ),
    ),
]
