from django.contrib import admin

# Register your models here.

from .models import Pergunta, Resposta

admin.site.register(Pergunta)
admin.site.register(Resposta)