from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# ----------------------------
# Custom User Model
# ----------------------------
def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='files/avatars/default.png')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username


# ----------------------------
# Withdrawal Request Model
# ----------------------------
class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('approved', 'Підтверджено'),
        ('rejected', 'Відхилено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, null=True, blank=True)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def save(self, *args, **kwargs):
        if self.pk:
            previous = WithdrawalRequest.objects.get(pk=self.pk)
            if previous.status != self.status:
                if self.status == 'rejected':
                    self.user.balance += self.amount
                    self.user.save()

                    Transaction.objects.create(
                        user=self.user,
                        transaction_type='withdrawal',
                        amount=self.amount,
                        status='failed',
                        description='Заявку відхилено, кошти повернено'
                    )

                elif self.status == 'approved':
                    Transaction.objects.create(
                        user=self.user,
                        transaction_type='withdrawal',
                        amount=self.amount,
                        status='completed',
                        description='Заявку підтверджено адміністратором'
                    )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Вивід {self.amount}₴ від {self.user.username} ({self.get_status_display()})"


# ----------------------------
# Transaction Model
# ----------------------------
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Поповнення'),
        ('withdrawal', 'Вивід'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('completed', 'Завершено'),
        ('failed', 'Відхилено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)  # приклади: "MonoBank", "Картка ****1234", "Скрін"

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount}₴ — {self.user.username} ({self.get_status_display()})"
