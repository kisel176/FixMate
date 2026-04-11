from django.shortcuts import render

def chat(request):
    return render(request, "chat/ai_chat.html")