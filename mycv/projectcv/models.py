from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser


# Create your models here.

class Genre(models.Model):
    genre_name = models.CharField(max_length=100)

    def __str__(self):
        return "Genre_name: {0}".format(self.genre_name)

class Tag(models.Model):
    tag_title =  models.CharField(max_length=30, verbose_name="Tags")

    def __str__(self):
        return self.tag_title

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

class Book(models.Model):
    title= models.CharField(max_length=250)
    author= models.CharField(max_length=150)
    genre = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)]) # range marks 1-5

    def __str__(self):
        tags = [i.tag_title for i in self.tags.all()]
        genre_names = [g.genre_name for g in self.genre.all()] if self.genre.exists() else ["None"]
        genre_display = ", ".join(genre_names)

        return f"Title: {self.title} | Author: {self.author} | Genres: {genre_display} | Tags: {tags}"

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"


class UserManager(BaseUserManager):
    # create user
    def create_user(self, email, password=None):
        if not email: raise ValueError("User must have an email address")
        if not password: raise ValueError("User must have a password")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
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

