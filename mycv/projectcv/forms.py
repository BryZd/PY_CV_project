
from django import forms
from .models import Book, Tag, User, Genre


class BookForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)


    class Meta:
        model = Book
        fields = ["title", "author", "publisher", "blurb", "genre", "tags", "rating", "published_date", "ean", "isbn",
                  "author_bio", "image", "author_photo", "rating", "facebook_url", "instagram_url", "amazon_url"]

        widgets = {
            'blurb': forms.Textarea(attrs={'rows': 4}),
            'author_bio': forms.Textarea(attrs={'rows': 4}),
            'published_date': forms.DateInput(attrs={'type': 'date'})
        }

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ["email", "password"]