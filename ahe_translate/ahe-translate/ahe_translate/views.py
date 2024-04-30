from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ahe_translate
from ahe_translate.models import KeyMap
# Create your views here.

@api_view(["POST"])
def save_keymap(request):
    key_maps = [KeyMap(**item) for item in request.data]
    KeyMap.objects.bulk_create(key_maps,ignore_conflicts=True)
    return Response("ok")
