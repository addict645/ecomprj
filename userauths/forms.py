from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "username"}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"placeholder": "email"}))
    password1 = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "password"}))
    password2 = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Confirm password"}))
    
    class Meta:
        model = User
        fields = ['username', 'email']
    