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
    publisher = models.CharField(max_length=150, null=True, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)]) # range marks 1-5

    # Layout
    image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    ean = models.CharField(max_length=13, null=True, blank=True)
    isbn = models.CharField(max_length=17, null=True, blank=True)
    author_bio = models.TextField(null=True, blank=True)
    author_photo = models.ImageField(upload_to='author_photos/', null=True, blank=True)
    blurb = models.TextField(null=True, blank=True, help_text="Short description of the book")

    # Social Media Links
    facebook_url = models.URLField(max_length=200, null=True, blank=True, help_text="Facebook page URL")
    instagram_url = models.URLField(max_length=200, null=True, blank=True, help_text="Instagram page URL")
    amazon_url = models.URLField(max_length=200, null=True, blank=True, help_text="Amazon page URL")

    def __str__(self):
        tags = [i.tag_title for i in self.tags.all()]
        genre_names = [g.genre_name for g in self.genre.all()] if self.genre.exists() else ["None"]
        genre_display = ", ".join(genre_names)

        return f"Title: {self.title} | Author: {self.author} | Genres: {genre_display} | Tags: {tags}"

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def get_average_rating(self):
        """Calculate average rating from votes"""
        votes = self.vote_set.all()
        if votes.exists():
            total = sum(vote.rating for vote in votes)
            return round(total / votes.count(), 1) # Round to 1 decimal place
        return None

    def get_vote_count(self):
        """Get total number of votes"""
        return self.vote_set.count()

    def get_user_vote(self, user):
        """Get specific user's vote for this book"""
        if user.is_authenticated:
            try:
                return self.vote_set.get(user=user)
            except Vote.DoesNotExist:
                return None
        return None

    @property
    def display_rating(self):
        """Get rating for display - prioritize average of votes over manual rating"""
        avg_rating = self.get_average_rating()
        if avg_rating is not None:
            return avg_rating
        return self.rating # Fallback to manual rating if no votes



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


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book') # Ensures one vote per user per book
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

    def __str__(self):
        return f"{self.user.email} voted {self.rating}/5 for {self.book.title}"