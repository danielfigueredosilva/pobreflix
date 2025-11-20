from django.contrib import admin

# Register your models here.

from .models import Pergunta, Resposta, Cadastro, Filme

@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = ("user", "telefone")

@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data_lancamento", "avaliacao")

admin.site.register(Pergunta)
admin.site.register(Resposta)