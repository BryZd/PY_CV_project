
from django.urls import path
from . import views


urlpatterns = [
    path("", views.book_detail, name="Book detail"), # je potřeba zmenit jména (detail) souboru podle souborů!
]