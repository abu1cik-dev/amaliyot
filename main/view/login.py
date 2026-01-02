from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from main.forms import RegisterForm
from django.contrib import messages
from main.forms import CustomUserCreationForm


# Create your views here.

def login_view(request):
    # Agar foydalanuvchi allaqachon login bo'lsa
    if request.user.is_authenticated:
        return redirect('/')  # home sahifaga

    # GET yoki POST request
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/'  # next param yoki default /

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Saytga muvaffaqiyatli kirdingiz")
            return redirect(next_url)  # next sahifaga yo'naltirish
        else:
            return render(request, 'loging/login.html', {
                'error': "Username yoki password noto‘g‘ri",
                'next': next_url
            })

    else:
        # GET request bo'lsa, next parametrini olamiz
        next_url = request.GET.get('next', '/')
        return render(request, 'loging/login.html', {'next': next_url})
    


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Akkaunt muvaffaqiyatli yaratildi!")
            return redirect("/")
        else:
            # Har bir xatoni messages orqali yuborish
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()

    return render(request, "loging/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "👋 Siz hisobdan muvaffaqiyatli chiqdingiz")
        
    return redirect('/')
