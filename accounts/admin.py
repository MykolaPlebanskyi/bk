from django.contrib import admin
from .models import CustomUser, WithdrawalRequest, Transaction


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass  # Можеш додати list_display, search_fields тощо, якщо потрібно


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'card_number', 'created_at', 'status')
    list_filter = ('status',)
    actions = ['approve_withdrawals', 'reject_withdrawals']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('user__username',)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new and obj.transaction_type == 'deposit' and obj.status == 'completed':
            obj.user.balance += obj.amount
            obj.user.save()
