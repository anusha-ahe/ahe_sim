from ahe_translate.views import save_keymap

from django import urls

from django.urls import path, include
# from ahe_sys.router import ahe_sys_router

app_name = "ahe_translate"

urlpatterns = [
    path('keymap', save_keymap,name="keymap"),

]
