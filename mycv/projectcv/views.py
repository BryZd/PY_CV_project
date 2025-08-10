from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import Book, User, Genre
from .forms import BookForm, UserForm, LoginForm

# Create your views here.
class BookIndex(generic.ListView):
    template_name = "projectcv/book_index.html"  # cesta k šabloně ze složky tamplates (je možné sdílet mezi aplikacemi)
    context_object_name = "books"  # pod tímto jménem budeme volat seznam objektů v šabloně

    # tato metoda nám získává seznam knih seřazených od největšího id (9,8,7...)

    def get_queryset(self):
        qs = Book.objects.select_related("genre").order_by("-id")
        q = self.request.GET.get("q")
        author = self.request.GET.get("author")
        genre = self.request.GET.get("genre")
        rating = self.request.GET.get("rating")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        if author:
            qs = qs.filter(author=author)
        if genre:
            qs = qs.filter(genre_id=genre)
        if rating:
            qs = qs.filter(rating=rating)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["authors"] = (Book.objects.order_by("author").distinct().values_list("author", flat=True).distinct())
        ctx["genres"] = Genre.objects.order_by("genre_name")
        ctx["ratings"] = [1, 2, 3, 4, 5]
        ctx["current"] = {
            "q": self.request.GET.get("q", ""),
            "author": self.request.GET.get("author", ""),
            "genre": self.request.GET.get("genre", ""),
            "rating": self.request.GET.get("rating", ""),
        }
        return ctx

class CurrentBook(generic.DetailView):

    model = Book
    template_name = "projectcv/book_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            book = self.get_object()
        except:
            return redirect("book_index")
        return render(request, self.template_name, {"book": book})

    def post(self, request, pk):
        # Only allow admins to trigger edit/delete actions via POST
        if not request.user.is_authenticated or not getattr(request.user, "is_admin", False)
            messages.info(request, "Only the admin can edit books.")
            return redirect("book_index")

        if "edit" in request.POST:
            return redirect("edit_book", pk=self.get_object().pk)
        if "delete" in request.POST:
            self.get_object().delete()
            return redirect("book_index")
        return redirect("book_detail", pk=pk)

class AddBook(generic.edit.CreateView):

    form_class = BookForm
    template_name = "projectcv/add_book.html"

#Metoda pro GET request, zobrazí pouze formulář
    def get(self, request):
        if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
            messages.info(request, "Only the admin can add books.")
            return redirect("book_index")
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

# Metoda pro POST request, zkontroluje formulář; pokud je validní, vytvoří novou knihu; pokud ne, zobrazí formulář s chybovou hláškou
    def post(self, request):
        if not request.user.is_authenticated or not getattr(request.user, "is_admin", False):
            messages.info(request, "Only the admin can add books.")
            return redirect("book_index")
        form = self.form_class(request.POST)
        if form.is_valid():
            book = form.save()
        return redirect("book_detail", pk=book.pk)

class EditBook(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView):
    model = Book
    form_class = BookForm
    template_name = "projectcv/add_book.html"
    context_object_name = "book"

    # Only admin can edit
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "is_admin", False)

    # Message + redirect when not permitted
    def handle_no_permission(self):
        messages.info(self.request, "Only the admin can edit books.")
        return redirect("book_index")

    # Ensure we fetch the book we're trying to edit
    def get_object(self, queryset=None):
        return get_object_or_404(Book, pk=self.kwargs.get("pk"))

    # After a successful POST, redirect to the detail page
    def get_success_url(self):
        return reverse("book_detail", kwargs={"pk": self.object.pk})


class UserViewRegister(generic.edit.CreateView):
    form_class = UserForm
    model = User
    template_name = "projectcv/user_form.html"

    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in, you cannot register.")
            return redirect("book_index")
        else:
            form = self.form_class(None)
        return render(request,self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            messages.info(request,"You are already logged in; you cannot register.")
            return redirect("book_index")
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect("book_index")

        return render(request, self.template_name, {"form": form})

class UserViewLogin(generic.edit.CreateView):
    form_class = LoginForm
    template_name = "projectcv/user_form.html"

    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in; you cannot log in again.")
            return redirect("book_index")
        else:
            form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in; you cannot log in again.")
            return redirect("book_index")
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect("book_index")
            else:
                messages.error(request, "This account doesn't exist")
        return render(request, self.template_name, {"form": form})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "You can't log out if you're not logged in.")
    return redirect("login")
