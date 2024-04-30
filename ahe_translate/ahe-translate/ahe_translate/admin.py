from fnmatch import translate
from django.contrib import admin
from .models import Hirarchy, Node, NodeVariable,Translation
# Register your models here.


admin.site.register(Hirarchy)
admin.site.register(NodeVariable)


class nodeAdmin(admin.ModelAdmin):
    list_display = ('name', '__str__', 'hirarchy',  'pattern', 'has_variables')
    list_filter = ('hirarchy', 'has_variables')


admin.site.register(Node, nodeAdmin)

admin.site.register(Translation)