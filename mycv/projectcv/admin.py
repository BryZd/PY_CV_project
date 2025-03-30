from django.contrib import admin
from django import forms


from .models import Book, Genre, User, UserManager, Tag
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField





class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def save(self, commit=True):
        if self.is_valid():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password"])
            if commit:
                user.save()
            return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "is_admin"]

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.Meta.fields.remove("password")


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
            "fields": ["email", "password"]}
        ),
    )
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

# Register your models here.

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(User, Admin)
admin.site.register(Tag)