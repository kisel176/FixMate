from django.shortcuts import render

def login(request):
    return render(request, "user/login.html")

def registr(request):
    return render(request, "user/registr.html")

def profile(request):
    return render(request, "user/profile.html")

