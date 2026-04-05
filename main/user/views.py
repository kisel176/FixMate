from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import UserLoginForm, UserRegistrationForm, UserChangeForm


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
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
                form.save()
                user = form.instance
                auth.login(request,user)

                messages.success(request, f"{user.username}, Вы успешно зарегистрировались в аккаунт")
                return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, "user/registr.html", context)

def profile(request):
    if request.method == 'POST' and 'image' in request.FILES:
        # Только загрузка аватарки
        user = request.user

        # Удаляем старую если есть
        if user.image:
            user.image.delete(save=False)

        # Сохраняем новую
        user.image = request.FILES['image']
        user.save()

        return redirect('user:profile')
    if request.method == 'POST':
        form = UserChangeForm(
            data=request.POST,
            files=request.FILES,  # Важно для загрузки изображений!
            instance=request.user
        )
        if form.is_valid():
            user = form.save(commit=False)
            # Если введен новый пароль
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, "Профиль успешно обнавлён")
            return redirect('user:profile')
    else:
        form = UserChangeForm(instance=request.user)
    context = {
            'form': form,
            'user': request.user,
    }

    return render(request, "user/profile.html", context)

