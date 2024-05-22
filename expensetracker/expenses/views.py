

from rest_framework.decorators import api_view
from rest_framework.response import Response 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@api_view()
def index(request):
    return Response("Hello World")

@api_view()
def get_expenses(request):
    return Response('Hello world')



