from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=200, required=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']