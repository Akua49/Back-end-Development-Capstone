from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password
