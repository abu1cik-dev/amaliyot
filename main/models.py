from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone


# =========================
# Custom User
# =========================
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username


# =========================
# Notice Model
# =========================

class Notice(models.Model):
    # 👑 Egasi
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notices"
    )

    # 📝 Asosiy ma'lumotlar
    title = models.CharField(max_length=200)
    main_text = models.TextField()

    # 🌍 Public / private link
    is_public = models.BooleanField(default=False)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # 👁 Ko‘rish statistikasi
    views = models.PositiveIntegerField(default=0)
    public_views = models.PositiveIntegerField(default=0)

    # 📥 Download / view limit (faqat public link uchun)
    download_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Public link orqali nechta odam ko‘ra oladi"
    )

    # ⏳ Amal qilish muddati (ixtiyoriy)
    expire_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Shu sanadan keyin link ishlamaydi"
    )

    # 🔄 Link holati
    is_active = models.BooleanField(default=True)

    # 🕒 Vaqtlar
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # =====================
    # 🔹 METODLAR
    # =====================
    def is_expired(self):
        """Link muddati tugaganmi?"""
        return self.expire_date and timezone.now() > self.expire_date

    def __str__(self):
        return f"{self.title} ({self.owner.username})"
    class Meta:
        ordering = ['-created_at']


# =========================
# Uploaded File Model
# =========================
import uuid
from django.db import models
from django.conf import settings

class UploadedFile(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files'
    )

    title = models.CharField(max_length=200)

    file = models.FileField(
        upload_to='uploads/files/',
        blank=True,   # 🔥 EDIT paytida muammo bo‘lmasin
        null=True
    )

    size = models.PositiveIntegerField(blank=True, null=True)

    is_public = models.BooleanField(default=False)

    # 🔥 public_id faqat public fayllar uchun ishlatiladi
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=True,
        blank=True
    )

    expire_date = models.DateTimeField(blank=True, null=True)

    views_count = models.PositiveIntegerField(default=0)
    download_limit = models.PositiveIntegerField(null=True, blank=True)
    downloaded_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Fayl o‘zgargan bo‘lsa size yangilanadi
        if self.file:
            try:
                if not self.pk or UploadedFile.objects.get(pk=self.pk).file != self.file:
                    self.size = self.file.size
            except UploadedFile.DoesNotExist:
                self.size = self.file.size

        # Har bir faylga public_id beramiz (private ham)
        if not self.public_id:
            self.public_id = uuid.uuid4()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class FileViewLog(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)


class FileDownloadLog(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='download_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

# =========================
# Uploaded Image Model
# =========================
class UploadedImage(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='images'
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='uploads/images/')

    is_public = models.BooleanField(default=False)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    allowed_users = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='allowed_images'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


# =========================
# Access Request Model
# =========================
class AccessRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    notice = models.ForeignKey(
        Notice, null=True, blank=True, on_delete=models.CASCADE
    )
    file = models.ForeignKey(
        UploadedFile, null=True, blank=True, on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        UploadedImage, null=True, blank=True, on_delete=models.CASCADE
    )

    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notice', 'file', 'image')
        ordering = ['-created_at']
