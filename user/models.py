from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('Mobile number is required')
        
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(mobile_number, password, **extra_fields)

def user_profile_picture_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/profile_pictures/user_<mobile_number>/<filename>
    return f"profile_pictures/user_{instance.mobile_number}/{filename}"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Mobile number must be 10 digits starting with 6, 7, 8, or 9"
    )
    
    mobile_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[mobile_validator],
        help_text="10-digit Indian mobile number"
    )
    alternate_mobile_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[mobile_validator],
        help_text="10-digit Indian alternate mobile number"
    )
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.mobile_number
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, help_text="Address label like 'Home', 'Office'")
    address = models.TextField(help_text="Full address")
    pincode = models.CharField(max_length=6, validators=[RegexValidator(regex=r'^\d{6}$', message="Pincode must be 6 digits")])
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.mobile_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
