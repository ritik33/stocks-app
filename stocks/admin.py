from django.contrib import admin
from .models import Investor, Stock, Order, Watchlist


admin.site.register(Investor)
admin.site.register(Stock)
admin.site.register(Order)
admin.site.register(Watchlist)
