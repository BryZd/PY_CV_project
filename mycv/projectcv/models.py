from django.db import models

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




