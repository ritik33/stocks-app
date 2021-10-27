from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.deletion import SET_NULL


class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=10000000)

    def __str__(self):
        return self.user.username


class Stock(models.Model):
    investor = models.ForeignKey("Investor", on_delete=models.CASCADE)
    symbol = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    buy_time = models.TimeField(auto_now_add=True)
    buy_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.symbol + ' ' + self.investor.user.username

    @property
    def total_price(self):
        total = self.price * self.quantity
        return total


class Order(models.Model):
    investor = models.ForeignKey("Investor", on_delete=models.CASCADE)
    stock = models.ForeignKey("Stock", on_delete=models.CASCADE)
    message = models.CharField(max_length=100, default='order message')

    def __str__(self):
        return self.stock.symbol + ' ' + self.investor.user.username


class Watchlist(models.Model):
    investor = models.ForeignKey("Investor", on_delete=models.CASCADE)
    stock = models.CharField(max_length=100)

    def __str__(self):
        return self.stock + ' ' + self.investor.user.username
