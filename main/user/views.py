from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import UserLoginForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)

            session_key = request.session.session_key

            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Вы вошли в аккаунт")
                if request.POST.get('next', None):
                    return HttpResponseRedirect(request.POST('next'))
                return HttpResponseRedirect(reverse('user:registr'))
    else:
        form = UserLoginForm()
    context = {
        'form' : form
    }
    return render(request, "user/login.html", context)

def registr(request):
    return render(request, "user/registr.html")

def profile(request):
    return render(request, "user/profile.html")

