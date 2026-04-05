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

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'image', 'bio', 'website', 'github', 'linkedin')

    first_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailInput()
    image = forms.ImageField()
    bio = forms.Textarea()
    website = forms.URLField(required=False)
    github = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Делаем все поля необязательными
        for field_name, field in self.fields.items():
            field.required = False

        # Для username особый случай - он readonly, но должен быть необязательным
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].required = False

        # Добавляем класс form-control если его нет
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 500:
            raise forms.ValidationError('Биография не может быть длиннее 500 символов')
        return bio

    def clean_username(self):
        # Защита: username нельзя изменить
        if self.instance and self.instance.pk:
            return self.instance.username
        return self.cleaned_data.get('username')