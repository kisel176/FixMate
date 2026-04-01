from django.shortcuts import render

def main(request):
    return render(request, "fixmate/main.html")

def ai(request):
    return render(request, "fixmate/ai.html")