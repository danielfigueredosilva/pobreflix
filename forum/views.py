from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.utils import timezone
from django.urls import reverse
from .models import Pergunta, Resposta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import Filme, Cadastro


# -------------------
# REGISTRO DE USUÁRIO
# -------------------
@csrf_exempt
def registrar(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método inválido"}, status=400)

    data = json.loads(request.body)
    email = data.get("email")
    senha = data.get("senha")

    if User.objects.filter(username=email).exists():
        return JsonResponse({"erro": "Usuário já existe"}, status=400)

    user = User.objects.create_user(username=email, password=senha)

    Cadastro.objects.create(user=user)

    return JsonResponse({"msg": "Usuário cadastrado com sucesso"})
    

# -------------------
# LOGIN COM SESSÃO
# -------------------
@csrf_exempt
def fazer_login(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método inválido"}, status=400)

    data = json.loads(request.body)
    email = data.get("email")
    senha = data.get("senha")

    user = authenticate(username=email, password=senha)

    if not user:
        return JsonResponse({"erro": "Credenciais inválidas"}, status=400)

    login(request, user)
    return JsonResponse({"msg": "Login realizado"})
    

# -------------------
# LOGOUT
# -------------------
def fazer_logout(request):
    logout(request)
    return JsonResponse({"msg": "Logout realizado"})


# -------------------
# LISTAR FILMES
# -------------------
def listar_filmes(request):
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Não autorizado"}, status=401)

    filmes = list(Filme.objects.all().values())
    return JsonResponse(filmes, safe=False)


# -------------------
# CRIAR FILME
# -------------------
@csrf_exempt
def criar_filme(request):
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Não autorizado"}, status=401)

    if request.method != "POST":
        return JsonResponse({"erro": "Método inválido"}, status=400)

    data = json.loads(request.body)

    Filme.objects.create(
        titulo=data["titulo"],
        descricao=data["descricao"],
        poster=data["poster"],
        data_lancamento=data["data_lancamento"],
        avaliacao=data["avaliacao"],
    )

    return JsonResponse({"msg": "Filme criado"})


class MainView(View):
    def get(self, request):
        perguntas = Pergunta.objects.order_by("-data_criacao")
        contexto = {'perguntas': perguntas}
        return render(request, 'forum/index.html', contexto)


class PerguntaView(View):
    def get(self, request, pergunta_id):
        pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
        contexto = {'pergunta': pergunta}
        return render(request, 'forum/detalhe.html', contexto)


class VotoView(View):
    def get(self, request, resposta_id):
        resposta = get_object_or_404(Resposta, pk=resposta_id)
        return HttpResponse(f"{resposta}; votos: {resposta.votos}")

    def post(self, request, resposta_id):
        resposta = get_object_or_404(Resposta, pk=resposta_id)
        resposta.votos += 1
        resposta.save()
        return redirect(reverse('forum:detalhe', args=[resposta.pergunta.id]))


class InserirPerguntaView(View):
    def get(self, request):
        return render(request, 'forum/inserir_pergunta.html')

    def post(self, request):
        usuario = request.user.username if request.user.is_authenticated else "anônimo"

        titulo = request.POST.get('titulo', '').strip()
        detalhe = request.POST.get('detalhe', '').strip()
        tentativa = request.POST.get('tentativa', '').strip()

        # validação simples
        if not titulo:
            return render(request, 'forum/inserir_pergunta.html', {
                'erro': 'O título não pode estar vazio.'
            })

        pergunta = Pergunta.objects.create(
            titulo=titulo,
            detalhe=detalhe,
            tentativa=tentativa,
            usuario=usuario,
            data_criacao=timezone.now()
        )

        return redirect(reverse('forum:detalhe', args=[pergunta.id]))


class InserirRespostaView(View):
    def get(self, request, pergunta_id):
        pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
        return render(request, 'forum/inserir_resposta.html', {'pergunta': pergunta})

    def post(self, request, pergunta_id):
        pergunta = get_object_or_404(Pergunta, pk=pergunta_id)

        usuario = request.user.username if request.user.is_authenticated else "anônimo"
        texto = request.POST.get('texto', '').strip()

        # evitar resposta vazia
        if not texto:
            return render(request, 'forum/inserir_resposta.html', {
                'pergunta': pergunta,
                'erro': "A resposta não pode estar vazia."
            })

        pergunta.resposta_set.create(
            texto=texto,
            usuario=usuario,
            data_criacao=timezone.now()
        )

        return redirect(reverse('forum:detalhe', args=[pergunta.id]))
