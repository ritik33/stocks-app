from django.urls import path
from . import views


urlpatterns = [
    path('', views.homePage, name='home'),
    path('stocks/', views.stocks, name='stocks'),
    path('stock-detail/<str:symbol>/', views.stockDetail, name='stock-detail'),
    path('top-gainers/', views.topGainers, name='top-gainers'),
    path('top-losers/', views.topLosers, name='top-losers'),
    path('sign-up/', views.signUp, name='sign-up'),
    path('sign-in/', views.signIn, name='sign-in'),
    path('sign-out/', views.signOut, name='sign-out'),
    path('profile/', views.profile, name='profile'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('buy/<str:symbol>/', views.buy, name='buy'),
    path('sell/<str:symbol>/<int:pk>/', views.sell, name='sell'),
    path('orders/', views.orders, name='orders'),
    path("watchlist/", views.watchlistPage, name="watchlist-page"),
    path('watchlist/<str:symbol>/', views.watchlist, name='watchlist'),
    path('s/', views.search, name='search'),
]
