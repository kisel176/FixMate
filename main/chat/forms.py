from django import forms
from .models import Chat, Message


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название чата'
            })
        }


class MessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'chat-input',
            'placeholder': 'Введите сообщение...',
            'rows': 3
        }),
        label=''
    )


class CodeAnalysisForm(forms.Form):
    code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'code-editor',
            'placeholder': 'Вставьте код для анализа...',
            'rows': 10
        }),
        label=''
    )
    language = forms.ChoiceField(
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('java', 'Java'),
            ('cpp', 'C++'),
        ],
        initial='python',
        widget=forms.Select(attrs={'class': 'form-select'})
    )