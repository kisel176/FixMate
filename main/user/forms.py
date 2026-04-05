from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    username = forms.CharField()
    password = forms.CharField()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    username = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2')

class UserChangeForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'image')

    first_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    image = forms.ImageField()
    bio = forms.Textarea()
    website = forms.URLField()
    github = forms.URLField()
    linkedin = forms.URLField()
