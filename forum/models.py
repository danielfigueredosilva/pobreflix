from django.db import models
import datetime
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CadastroManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Cadastro(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CadastroManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class FilmeFavorito(models.Model):
    user = models.ForeignKey(Cadastro, on_delete=models.CASCADE, related_name="favoritos")
    filme_id = models.IntegerField()  # ou vincular a um model Filme, se tiver
    titulo = models.CharField(max_length=200)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.user.email}"




class Pergunta(models.Model):
    titulo = models.CharField(max_length=200, null=False)
    detalhe = models.TextField(null=False)
    tentativa = models.TextField()
    data_criacao = models.DateTimeField("Criado em ")
    usuario = models.CharField(max_length=200, null=False, default="anônimo")

    def __str__(self):
        return "[" + str(self.id) + "] " + self.titulo
    
    def foi_publicado_recentemente(self):
        return self.data_criacao >= timezone.now() - datetime.timedelta(days=1)

    def string_detalhada(self):
        return "id: " + str(self.id) + "; titulo: " + self.titulo + "; detalhe: " + self.detalhe + "; tentativa: " + self.tentativa + "; data criação: " + str(self.data_criacao) + "; usuario: " + self.usuario


class Resposta(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    texto = models.TextField(null=False)
    votos = models.IntegerField(default=0)
    data_criacao = models.DateTimeField("Criado em ")
    usuario = models.CharField(max_length=200, null=False, default="anônimo")


    def __str__(self):
        return "[" + str(self.id) + "] " + self.texto
    
    def foi_publicado_recentemente(self):
        return self.data_criacao >= timezone.now() - datetime.timedelta(days=1)