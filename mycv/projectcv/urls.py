
from django.urls import path
from . import views


urlpatterns = [
    path("", views.detail_souboru, name="projectcv_detail_souboru"), # je potřeba zmenit jména (detail) souboru podle souborů!
]