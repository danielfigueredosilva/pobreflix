from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.utils import timezone
from django.urls import reverse

from .models import Pergunta, Resposta


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
