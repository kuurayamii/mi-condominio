from django.shortcuts import render
from django.http import HttpResponse


# TODO: Borrar esta vista después cuando ya no sea necesaria
# def index(response):
#     return HttpResponse("Hola, estas en el indice de micondominio")


def landing(request):
    """Vista de la landing page"""
    return render(request, 'mi_condominio/landing.html')

