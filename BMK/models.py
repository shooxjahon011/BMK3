from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # Rasm va video uchun (null=True bo'lishi shart, chunki har doim ham yuklanmasligi mumkin)
    image = models.ImageField(upload_to='announcements/images/', null=True, blank=True)
    video = models.FileField(upload_to='announcements/videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at'] # Yangi xabarlar tepada chiqadi

    def __str__(self):
        return self.title


# 1. Avval Neighborhood klassi bo'lishi shart
class Neighborhood(models.Model):
    name = models.CharField(max_length=100, verbose_name="Mahalla nomi")
    # Har bir mahallaga biriktirilgan loyiha ID raqami
    project_id = models.CharField(max_length=20, verbose_name="Loyiha ID raqami", default="000000")
    votes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

# 2. Keyin esa Voter klassi, chunki u yuqoridagi klassga tayanadi
class Voter(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13, unique=True)
    age = models.IntegerField()
    # Bu yerda Neighborhood tepada aniqlangan bo'lishi kerak
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    is_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.phone}"


class DailyStats(models.Model):
    date = models.DateField(unique=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date}: {self.count} ovoz"
class UserProfile(models.Model):
    full_name = models.CharField(max_length=255)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # Hashlangan bo'lishi kerak
    phone = models.CharField(max_length=20)
    mahalla = models.CharField(max_length=100, blank=True, null=True)
    kocha = models.CharField(max_length=100, blank=True, null=True)
    uy_raqami = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active_session = models.BooleanField(default=False)  # Kirgan-kirmaganini tekshirish uchun
    device_id = models.CharField(max_length=255, null=True, blank=True)
    neighborhood = models.ForeignKey('Neighborhood', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        role = "Boshliq" if self.is_boss else "Ishchi"
        return self.full_name
class Vote(models.Model):
    # Foydalanuvchi bilan bog'laymiz
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.created_at}"