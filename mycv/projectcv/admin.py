from django.contrib import admin
from django import forms

from .models import Book, Genre, User, Tag
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Password")

    class Meta:
        model = User
        fields = ["email", "password", "is_admin"]


class Admin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["email", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Permission", {"fields": ["is_admin"]}),
    )

    add_fieldsets = (
        (None, {
            "fields": ["email", "password1", "password2"],
        }),
    )
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publisher', 'get_genres', 'rating']
    list_filter = ['genre', 'rating', 'published_date']
    search_fields = ['title', 'author', 'publisher']
    filter_horizontal = ('genre', 'tags')

    fieldsets = (
        ('Basic Information',{
            'fields': ('title', 'author', 'publisher', 'rating')
        }),
        ('Content', {
            'fields': ('blurb', 'author_bio')
        }),
        ('Publication Details', {
            'fields': ('published_date', 'ean', 'isbn')
        }),
        ('Media', {
            'fields': ('image', 'author_photo')
        }),
        ('Categories', {
            'fields': ('genre', 'tags')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'amazon_url')
        })
    )

    def get_genres(self, obj):
        return", ".join([genre.genre_name for genre in obj.genre.all()])
    get_genres.short_description = 'Genres'


admin.site.register(Genre)
admin.site.register(User, Admin)
admin.site.register(Tag)