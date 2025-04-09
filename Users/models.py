from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# ===========================
# Custom User Manager
# ===========================
class UserManager(BaseUserManager):
    def create_user(self, password=None, pin=None, **extra_fields):
        user_id = None
        if 'user_id' in extra_fields:
            user_id = extra_fields['user_id']
            del extra_fields['user_id']
        else:
            candidate = User.objects.count() + 1
            while True:
                if not User.objects.filter(user_id=candidate).exists():
                    break
                candidate += 1
            user_id = candidate

        user = self.model( pin=pin, user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, password, pin=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(password, pin, **extra_fields)

# ===========================
# User Model
# ===========================
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50, unique=True,primary_key=True)
    pin = models.CharField(max_length=10,blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    email_address = models.EmailField(blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['pin']

    def __str__(self):
        return self.name
