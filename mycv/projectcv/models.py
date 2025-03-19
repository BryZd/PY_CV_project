from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class Genre(models.Model):
    genre_name = models.CharField(max_length=100)

    def __str__(self):
        return "Genre_name: {0}".format(self.genre_name)


class Book(models.Model):
    title= models.CharField(max_length=250)
    author= models.CharField(max_length=150)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Title: {0} | Author: {1} | Genre: {2}".format(self.title, self.author, self.genre.genre_name)


class UserManager(BaseUserManager):
    # create user
    def create_user(self, email, password):
        print(self.model)
        if email and password:
            user = self.model(email=self.normalize_email(email))
            user.set_password(password)
            user.save()
            return user

    # create admin
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save()
        return user


class User(AbstractBaseUser):

    email = models.EmailField(max_length=300, unique=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return "email: {}".format(self.email)

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

