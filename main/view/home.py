from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.forms import CustomUserUpdateForm


# Create your views here.

def home(request):
    return render(request, 'index.html')

def account(request):
    user = request.user  # CustomUser instansiyasi

    context = {
        "user": user,  # bu oddiy user objektini uzatamiz
        "user_agent": request.META.get('HTTP_USER_AGENT', 'Noma’lum qurilma'),
    }


    return render(request, "acount.html")
