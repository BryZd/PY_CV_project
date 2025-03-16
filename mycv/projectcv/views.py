from django.shortcuts import render
from django.views import generic

from .models import Book
from .forms import BookForm

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

class AddBook(generic.edit.CreateView):

    form_class = BookForm
    template_name = "projectcv/add_book.html"

#Metoda pro GET request, zobrazí pouze formulář
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

# Metoda pro POST request, zkontroluje formulář; pokud je validní, vytvoří novou knihu
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
        return render(request, self.template_name, {"form": form})