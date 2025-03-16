from django.shortcuts import render

# Create your views here.

def book_detail(request):
    return render(request, "projectcv/book_detail.html", dict(book_title="něco", genre="fantasy", status="read"))
