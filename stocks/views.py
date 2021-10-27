from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Investor, Stock, Order, Watchlist
from nsetools import Nse
import decimal
nse = Nse()


def homePage(request):
    return render(request, 'index.html')


def stocks(request):
    all_stock_codes = nse.get_stock_codes()
    context = {'stocks': all_stock_codes}
    return render(request, 'stocks.html', context)


def stockDetail(request, symbol):
    stock = nse.get_quote(symbol)
    context = {'stock': stock}
    return render(request, 'stock-detail.html', context)


def topGainers(request):
    top_gainers = nse.get_top_gainers()
    context = {'top_gainers': top_gainers}
    return render(request, 'top-gainers.html', context)


def topLosers(request):
    top_losers = nse.get_top_losers()
    context = {'top_losers': top_losers}
    return render(request, 'top-losers.html', context)


def signUp(request):
    if request.user.is_authenticated:
        messages.success(request, 'You are already signed up')
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            investor = Investor(user=user)
            investor.save()
            messages.success(request, 'Successfully signed up')
            return redirect('sign-in')
        messages.info(request, 'Invalid form submission')
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'sign-up.html', context)


def signIn(request):
    if request.user.is_authenticated:
        messages.success(request, 'You are already signed in')
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Successfully signed in')
            return redirect('home')
        messages.info(request, 'Invalid form submission')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'sign-in.html', context)


@login_required(login_url='sign-in')
def signOut(request):
    logout(request)
    messages.success(request, 'Signed Out')
    return redirect('home')


@login_required(login_url='sign-in')
def profile(request):
    investor = Investor.objects.get(pk=request.user.id)
    context = {'investor': investor}
    return render(request, 'profile.html', context)


@login_required(login_url='sign-in')
def portfolio(request):
    investor = Investor.objects.get(pk=request.user.id)
    stocks = Stock.objects.filter(investor=investor)
    context = {'investor': investor, 'stocks': stocks}
    return render(request, 'portfolio.html', context)


@login_required(login_url='sign-in')
def buy(request, symbol):
    investor = Investor.objects.get(pk=request.user.id)
    buyStock = nse.get_quote(symbol)
    if request.method == 'POST':
        amount = decimal.Decimal(
            buyStock['lastPrice']) * decimal.Decimal(request.POST['quantity'])
        if investor.balance < amount:
            messages.info(request, "You don't have enough balance to invest")
            return redirect('home')
        stock = Stock.objects.create(
            investor=investor, symbol=buyStock['symbol'], company_name=buyStock['companyName'],
            price=buyStock['lastPrice'], quantity=request.POST['quantity'])
        investor.balance -= amount
        investor.save(update_fields=['balance'])
        order = Order.objects.create(investor=investor, stock=stock, message="Buy order of {} share/s at price Rs {} of {} is completed".format(
            stock.quantity, stock.price, stock.company_name))
        messages.success(
            request, 'You have successfully completed your investment')
        return redirect('home')
    else:
        context = {'stock': buyStock}
        return render(request, 'buy.html', context)


@login_required(login_url='sign-in')
def sell(request, symbol, pk):
    investor = Investor.objects.get(pk=request.user.id)
    stock = Stock.objects.get(pk=pk)
    lastPrice = nse.get_quote(symbol)['lastPrice']
    if request.method == 'POST':
        sellQuantity = int(request.POST['quantity'])
        if sellQuantity == stock.quantity:
            investor.balance += stock.total_price
            investor.save(update_fields=['balance'])
            stock.delete()
        elif sellQuantity > stock.quantity:
            messages.info(request, "You can't sell more than what you have")
            return redirect('home')
        else:
            oldTotal = stock.total_price
            order = Order.objects.create(investor=investor, stock=stock, message="Sell order of {} share/s at price Rs {} of {} is completed".format(
                sellQuantity, lastPrice, stock.company_name))
            stock.quantity -= sellQuantity
            stock.save(update_fields=['quantity'])
            newTotal = stock.total_price
            investor.balance += oldTotal - newTotal
            investor.save(update_fields=['balance'])
        messages.success(request, 'You have successfully sold your stocks')
        return redirect('home')
    else:
        context = {'stock': stock, 'investor': investor,
                   'lastPrice': lastPrice}
        return render(request, 'sell.html', context)


@login_required(login_url='sign-in')
def orders(request):
    orders = Order.objects.filter(investor_id=request.user.id)
    context = {'orders': orders[::-1]}
    return render(request, 'orders.html', context)


@login_required(login_url='sign-in')
def watchlist(request, symbol):
    investor = Investor.objects.get(pk=request.user.id)
    stock_to_watch = nse.get_quote(symbol)
    watchStock, created = Watchlist.objects.get_or_create(
        investor=investor, stock=stock_to_watch['symbol'])
    print(watchStock, created)
    if created:
        messages.success(request, 'You have added {} stock in watchlist'.format(
            stock_to_watch['companyName']))
        return redirect('stocks')
    else:
        watchStock.delete()
        messages.success(request, 'You have removed {} stock from watchlist'.format(
            stock_to_watch['companyName']))
        return redirect('stocks')


@login_required(login_url='sign-in')
def watchlistPage(request):
    investor = Investor.objects.get(pk=request.user.id)
    watchlists = Watchlist.objects.filter(investor=investor)
    context = {'watchlists': watchlists[::-1]}
    return render(request, 'watchlist.html', context)


def search(request):
    query = request.GET['search']
    if nse.is_valid_code(query):
        stock = nse.get_quote(query)
        context = {'stock': stock}
        return render(request, 'search.html', context)
    else:
        messages.info(request, 'You entered an invalid symbol')
        return redirect('stocks')
