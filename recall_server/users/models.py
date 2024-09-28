# """
# This module defines models for the user accounts.
# """
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
# from django.db import models

# class UserManager(BaseUserManager):
#     """
#     Custom user manager for User model with email as the unique identifier.
#     """

#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("users must have an email address")
#         user = self.model(
#             email=self.normalize_email(email),
#             **extra_fields,
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         user.is_active = True
#         return user
    
#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         # extra_fields.setdefault('is_superuser', True)

#         return self.create_user(email, password, **extra_fields)

# class User(AbstractBaseUser, PermissionsMixin):
#     """ User model representing custom user accounts for the project. """

#     id_number = models.CharField(max_length=8, default=None)
#     profile_pic = models.URLField(default="https://cdn.pixabay.com/photo/2021/07/25/08/03/account-6491185_1280.png")
#     email = models.EmailField(unique=True)
#     is_voter = models.BooleanField(default=True)
#     is_leader = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["id_number"]

#     objects = UserManager()
    
#     def __str__(self):
#         return f"{self.email} {self.id_number}"


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the unique identifier.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model where email is the unique identifier for authentication instead of usernames.
    """
    id_number = models.CharField(max_length=8, unique=True)
    profile_pic = models.URLField(default="https://cdn.pixabay.com/photo/2021/07/25/08/03/account-6491185_1280.png")
    email = models.EmailField(unique=True)
    is_voter = models.BooleanField(default=True)
    is_leader = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["id_number"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} {self.id_number}"
