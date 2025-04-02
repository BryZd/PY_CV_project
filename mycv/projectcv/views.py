from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Book, User
from .forms import BookForm, UserForm, LoginForm

# Create your views here.
class BookIndex(generic.ListView):
    template_name = "projectcv/book_index.html"  # cesta k šabloně ze složky tamplates (je možné sdílet mezi aplikacemi)
    context_object_name = "books"  # pod tímto jménem budeme volat seznam objektů v šabloně

    # tato metoda nám získává seznam filmů seřazených od největšího id (9,8,7...)

    def get_queryset(self):
        return Book.objects.all().order_by("-id")

class CurrentBook(generic.DetailView):

    model = Book
    template_name = "projectcv/book_detail.html"

    def get(self, request, pk):
        try:
            film = self.get_object()
        except:
            return redirect("book_index")
        return render(request, self.template_name, {"film": film})

    def post(self, request, pk):
        if request.user.is_authenticated:
            if "edit" in request.POST:
                return redirect("edit_book", pk=self.get_object().pk)
            else:
                if not request.user.is_admin:
                    messages.info(request, "You cannot delete the book; you are not an admin")
                    return redirect("book_index")
                else:
                    self.get_object().delete()
        return redirect("book index")

class AddBook(generic.edit.CreateView):

    form_class = BookForm
    template_name = "projectcv/add_book.html"

#Metoda pro GET request, zobrazí pouze formulář
    def get(self, request):
        if not request.user.is_admin:
            messages.info(request, "Only the admin can add books.")
            return redirect("book_index")
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

# Metoda pro POST request, zkontroluje formulář; pokud je validní, vytvoří novou knihu; pokud ne, zobrazí formulář s chybovou hláškou
    def post(self, request):
        if not request.user.is_admin:
            messages.info(request, "Only the admin can add books.")
            return redirect("book_index")
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
        return render(request, self.template_name, {"form": form})

class EditBook(LoginRequiredMixin,generic.edit.CreateView):
    form_class = BookForm
    template_name = "projectcv/add_book.html"

    def get(self,request, pk):
        if not request.user.is_admin:
            messages.info(request, "Only the admin can edit books.")
            return redirect("book_index")
        try:
            book = Book.objects.get(pk=pk)
        except:
            messages.error(request, "This book doesn't exist!")
            return redirect("book_index")
        form = self.form_class(instance=book)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk): # pokračování v lekci 11.


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
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("book_index")
        return render(request, self.template_name, {"form": form})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    else:
        messages.info(request, "You can't log out if you're not logged in.")
    return redirect("login")
