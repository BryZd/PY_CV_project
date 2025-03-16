
from django.urls import path
from . import views


urlpatterns = [
    path("book_index/", views.BookIndex.as_view(), name="book_index"),
    path("<int:pk>/book_detail/", views.CurrentBook.as_view(), name="book_detail"),
    path("add_book/", views.AddBook.as_view(), name="add_book"),
]