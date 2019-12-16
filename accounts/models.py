from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, username, contact_number, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        if not contact_number:
            raise ValueError("User must have a contact_number")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            contact_number = contact_number,
        )

        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, email, username, contact_number, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            contact_number = contact_number,
            password =password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        verified = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=10, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'contact_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class MobileVerification(models.Model):
    user = models.ForeignKey(User, related_name = 'user_to_send',on_delete=models.CASCADE)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} otp {}'.format(self.user, self.otp)

class Follower(models.Model):
    user_from = models.ForeignKey(User, related_name='user_following', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='user_followed', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return '{} follow {}'.format(self.user_from, self.user_to)

class Event(models.Model):
    type = models.CharField(max_length=255,unique=True)
    comment = models.CharField(max_length=255)

    def __str__(self):
        return self.comment

class Notification(models.Model):
    user_to_notify = models.ForeignKey(User, related_name = 'user_to_notify',on_delete=models.CASCADE)
    user_who_fired_event = models.ForeignKey(User, related_name= 'user_who_fired_event' ,on_delete=models.CASCADE)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    seen_by_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} {} {}'.format(self.user_who_fired_event, self.event_id ,self.user_to_notify)