from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import CustomUser, Notice, UploadedFile, UploadedImage


# =========================
# Custom User Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser  # yoki User, lekin CustomUser tavsiya qilinadi
        fields = ("username", "email", "password1", "password2")

# =========================
# Foydalanuvchini yaratish
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "user"  # avtomatik ROLE
        if commit:
            user.save()
        return user

# =========================
# Foydalanuvchi ma’lumotlarini tahrirlash
class CustomUserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email")  # kerak bo‘lsa role qo‘shish mumkin
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


# =========================
# Uploaded File Form
# =========================class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = [
            'title',
            'file',
            'is_public',
            'download_limit',   # 🔥 QO‘SHILDI
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Fayl sarlavhasini kiriting'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg'
            }),
            'download_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: 5',
                'min': 1
            }),
        }

# =========================
# Notice Form
# =========================
class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'main_text', 'is_public', 'expire_date', 'download_limit']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Eslatma sarlavhasini kiriting'
            }),
            'main_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Eslatma matnini kiriting',
                'rows': 5
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'expire_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'download_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maksimal ko‘rishlar soni'
            }),
        }
class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = [
            'title',
            'file',
            'is_public',
            'expire_date',
            'download_limit',   # 🔥 QO‘SHILDI
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'expire_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'download_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: 10 (bo‘sh = cheksiz)'
            }),
        }

        
# =========================
# Uploaded Image Form
# =========================
class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['title', 'image', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Rasm sarlavhasini kiriting'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-lg'
            }),
        } 
