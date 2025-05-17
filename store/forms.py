# store/forms.py

from django import forms
from .models import Order

class CheckoutForm(forms.Form):
    customer_name = forms.CharField(
        label="Nombre completo", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    customer_phone = forms.CharField(
        label="Teléfono", 
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label="Notas adicionales", 
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }