from django.shortcuts import render

# Create your views here.

def detail_souboru(request):
    return render(request, "projectcv/detail_souboru.html", dict(nazev_souboru="neco", kategorie="smlouva", stav="platná"))
