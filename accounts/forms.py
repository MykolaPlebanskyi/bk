# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import CustomUser, WithdrawalRequest


# -----------------------------
# Register Form
# -----------------------------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


# -----------------------------
# Profile Update Form
# -----------------------------
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']

# -----------------------------
# Withdrawal Request Form
# -----------------------------
class WithdrawForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'card_number']

    def clean_card_number(self):
        card = self.cleaned_data.get('card_number', '').replace(' ', '')
        if not card:
            raise forms.ValidationError("Поле не може бути порожнім.")
        if len(card) < 8:
            raise forms.ValidationError("Номер картки має містити щонайменше 8 цифр.")
        if not card.isdigit():
            raise forms.ValidationError("Номер картки повинен містити лише цифри.")
        return card

