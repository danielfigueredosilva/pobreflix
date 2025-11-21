import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Pergunta, Resposta, Filme, Cadastro
from .models import Filme


# REGISTRO DE USUÁRIO
@csrf_exempt
def registrar(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método inválido"}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"erro": "JSON inválido"}, status=400)

    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return JsonResponse({"erro": "email e senha obrigatórios"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"erro": "Usuário já existe"}, status=400)

    user = User.objects.create_user(username=email, password=senha)
    Cadastro.objects.create(user=user)
    return JsonResponse({"msg": "Usuário cadastrado com sucesso", "user": user.username})


# LOGIN / LOGOUT
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
    return JsonResponse({"msg": "Login realizado", "user": user.username})


def fazer_logout(request):
    logout(request)
    return JsonResponse({"msg": "Logout realizado"})


# LISTAR FILMES 
def listar_filmes(request):
    filmes = Filme.objects.all()
    lista = []
    for filme in filmes:
        lista.append({
            "id": filme.id,
            "titulo": filme.titulo,
            "descricao": filme.descricao,
            "poster": filme.poster,
            "data_lancamento": filme.data_lancamento.isoformat(),
            "avaliacao": filme.avaliacao,
            "user": filme.user.username if filme.user else None,  # evita erro se user for None
        })
    return JsonResponse(lista, safe=False)


# CRIAR FILME
@csrf_exempt
def criar_filme(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método inválido"}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"erro": "JSON inválido"}, status=400)

    try:
        data_lanc = datetime.strptime(data.get("data_lancamento", "2000-01-01"), "%Y-%m-%d").date()
    except:
        data_lanc = datetime(2000, 1, 1).date()

    try:
        avaliacao = float(data.get("avaliacao", 0))
    except:
        avaliacao = 0

    filme = Filme.objects.create(
        titulo=data.get("titulo", "Sem título"),
        descricao=data.get("descricao", ""),
        poster=data.get("poster", ""),
        data_lancamento=data_lanc,
        avaliacao=avaliacao,
        user=None  # permite criar sem usuário
    )

    return JsonResponse({"msg": "Filme criado com sucesso", "id": filme.id})


# Apagar filme
@csrf_exempt
def apagar_filme(request, filme_id):
    if request.method == 'DELETE':
        try:
            filme = Filme.objects.get(pk=filme_id)
            filme.delete()
            return JsonResponse({'message': 'Filme deletado'})
        except Filme.DoesNotExist:
            return JsonResponse({'error': 'Filme não encontrado'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)




class MainView(View):
    def get(self, request):
        perguntas = Pergunta.objects.order_by("-data_criacao")
        return render(request, 'forum/index.html', {'perguntas': perguntas})


class PerguntaView(View):
    def get(self, request, pergunta_id):
        pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
        return render(request, 'forum/detalhe.html', {'pergunta': pergunta})


class VotoView(View):
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

        if not titulo:
            return render(request, 'forum/inserir_pergunta.html', {'erro': 'O título não pode estar vazio.'})

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

        if not texto:
            return render(request, 'forum/inserir_resposta.html', {'pergunta': pergunta, 'erro': "A resposta não pode estar vazia."})

        pergunta.resposta_set.create(texto=texto, usuario=usuario, data_criacao=timezone.now())
        return redirect(reverse('forum:detalhe', args=[pergunta.id]))
