from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import RegisterForm, ProfileUpdateForm, WithdrawForm
from .models import WithdrawalRequest, Transaction


# -------------------------------
# АВТОРИЗАЦІЯ
# -------------------------------

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------------------
# ПРОФІЛЬ
# -------------------------------

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# -------------------------------
# БАЛАНС І ТРАНЗАКЦІЇ
# -------------------------------

@login_required
def balance_view(request):
    transactions = list(request.user.transactions.order_by('-created_at'))
    pending_withdrawals = list(
        request.user.withdrawals.filter(status='pending').order_by('-created_at')
    )

    for t in transactions:
        t.item_type = 'transaction'
        t.transaction_type_display = t.get_transaction_type_display()

    for w in pending_withdrawals:
        w.item_type = 'withdrawal'
        w.transaction_type_display = 'Вивід'

    all_items = sorted(transactions + pending_withdrawals, key=lambda x: x.created_at, reverse=True)

    paginator = Paginator(all_items, 10)  # 10 елементів на сторінку
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/balance.html', {'page_obj': page_obj})


# -------------------------------
# ВИВІД КОШТІВ
# -------------------------------

@login_required
def withdraw_view(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            card_number = form.cleaned_data['card_number']
            user = request.user

            if amount > user.balance:
                messages.error(request, 'Недостатньо коштів на балансі.')
            else:
                user.balance -= amount
                user.save()
                WithdrawalRequest.objects.create(
                    user=user,
                    amount=amount,
                    card_number=card_number
                )
                messages.success(request, 'Заявка на вивід створена. Очікуйте підтвердження адміном.')
                return redirect('balance')
    else:
        form = WithdrawForm()
    return render(request, 'accounts/withdraw.html', {'form': form})


@login_required
def cancel_withdrawal(request, pk):
    withdrawal = get_object_or_404(WithdrawalRequest, pk=pk, user=request.user)
    if withdrawal.status == 'pending':
        withdrawal.status = 'rejected'
        withdrawal.save()
    return redirect('balance')


# -------------------------------
# ІСТОРІЯ СТАВОК
# -------------------------------

@login_required
def bet_history_view(request):
    bets = request.user.bet_history.select_related('match', 'team').order_by('-created_at')
    return render(request, 'accounts/bet_history.html', {'bets': bets})
