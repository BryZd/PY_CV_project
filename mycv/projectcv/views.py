from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.views.generic import FormView

from .models import Book, User, Genre
from .forms import BookForm, UserForm, LoginForm


RATING_CHOICES = [(i, i) for i in range(1, 6)]
RATING_VALUES = [choice[0] for choice in RATING_CHOICES]

# Create your views here.
class BookIndex(generic.ListView):
    template_name = "projectcv/book_index.html"  # cesta k šabloně ze složky tamplates (je možné sdílet mezi aplikacemi)
    context_object_name = "books"  # pod tímto jménem budeme volat seznam objektů v šabloně



    def get_queryset(self):
        # Get filtered parameters from request
        qs = Book.objects.prefetch_related("genre").order_by("-id")
        q = self.request.GET.get("q")
        author = self.request.GET.get("author")
        genre = self.request.GET.get("genre")
        rating = self.request.GET.get("rating")

        # Apply filters if parameters exist
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        if author:
            qs = qs.filter(author=author)
        if genre:
            qs = qs.filter(genre__id=genre)
        if rating:
            qs = qs.filter(rating=rating)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["authors"] = Book.objects.order_by("author").values_list("author", flat=True).distinct()
        ctx["genres"] = Genre.objects.order_by("genre_name")
        ctx["ratings"] = RATING_VALUES
        ctx["current"] = {
            "q": self.request.GET.get("q", ""),
            "author": self.request.GET.get("author", ""),
            "genre": self.request.GET.get("genre", ""),
            "rating": self.request.GET.get("rating") or None,
        }
        return ctx

class CurrentBook(generic.DetailView):

    model = Book
    template_name = "projectcv/book_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            book = self.get_object()
        except (Book.DoesNotExist, Http404):
            return redirect("book_index")
        return render(request, self.template_name, {"book": book})

    def post(self, request, pk):
        # Only allow admins to trigger edit/delete actions via POST
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.info(request, "Only the admin can edit books.")
            return redirect("book_index")

        book = self.get_object()
        if "edit" in request.POST:
            return redirect("edit_book", pk=book.pk)
        if "delete" in request.POST:
            book.delete()
            return redirect("book_index")
        return redirect("book_detail", pk=pk)

class AddBook(UserPassesTestMixin, generic.edit.CreateView):

    form_class = BookForm
    template_name = "projectcv/add_book.html"

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.info(self.request, "Only the admin can add books.")
        return redirect("book_index")

#Metoda pro GET request, zobrazí pouze formulář
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

# Metoda pro POST request, zkontroluje formulář; pokud je validní, vytvoří novou knihu; pokud ne, zobrazí formulář s chybovou hláškou
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect("book_detail", pk=book.pk)
        return render(request, self.template_name, {"form": form})

class EditBook(LoginRequiredMixin, UserPassesTestMixin, generic.edit.UpdateView):
    model = Book
    form_class = BookForm
    template_name = "projectcv/add_book.html"
    context_object_name = "book"

    # Only admin can edit
    def test_func(self):
        return self.request.user.is_staff

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
    success_url= reverse_lazy("book_index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in, you cannot register.")
            return redirect("book_index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data["password"]
        user.set_password(password)
        user.save()
        login(self.request, user)
        return super().form_valid(form)


class UserViewLogin(FormView):
    form_class = LoginForm
    template_name = "projectcv/user_form.html"
    success_url = reverse_lazy("book_index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("book_index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(self.request, username=email, password=password)
            if user:
                login(self.request, user)
                return super().form_valid(form)
            else:
                form.add_error(None, "This account doesn't exist")
            return self.form_invalid(form)

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "You can't log out if you're not logged in.")
    return redirect("login")
