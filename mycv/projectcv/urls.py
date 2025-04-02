
from django.urls import path
from . import views
from . import url_handlers


urlpatterns = [
    path("book_index/", views.BookIndex.as_view(), name="book_index"),
    path("<int:pk>/book_detail/", views.CurrentBook.as_view(), name="book_detail"),
    path("add_book/", views.AddBook.as_view(), name="add_book"),
    path("<int:pk>/edit/", views.EditBook.as_view(), name="edit_book"),
    path("register/", views.UserViewRegister.as_view(), name="registration"),
    path("login/", views.UserViewLogin.as_view(), name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("", url_handlers.index_handler),
]