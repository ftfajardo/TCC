from .models import Fotos,NovasFotos,Dias,Recognition,Contador,Metodo,Vectors,Distancias_reais
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from . import utils
from django.db.models import F








def exclusao(request):
    """  Método que realiza exclusão dos dados de reconhecimento """
    if request.method == 'POST':
        if 'botao' in request.POST:
            data = str(request.POST.get('data'))
            executa_exclusao(data,request)

        if 'botao_total' in request.POST:
            exclusao_total(request)
    return redirect('rec')

def exclusao_total(request):

    if(Recognition.objects.all().count() > 0):
        try:
            Recognition.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar todos reconhecimentos")

    if(Contador.objects.all().count() > 0):
        try:
            Contador.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar todos os contadores")

    if (NovasFotos.objects.all().count() > 0):
        try:
            NovasFotos.objects.all().update(Reconhecida=False)
        except:
            messages.error(request, "não foi possivel setar false nas fotos ja reconhecidas")


    if (Vectors.objects.all().count() > 0):
        try:
            Vectors.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar vectors")


    if (Distancias_reais.objects.all().count() > 0):
        try:
            Distancias_reais.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar distancias reais")




def executa_exclusao(data,request):
    if data == "default":

        if(Recognition.objects.filter().values('foto_1').count() > 0):
            var = Recognition.objects.filter().values('foto_1')
            for i in var:
                foto = i.get('foto_1')
                try:
                    NovasFotos.objects.filter(novaimage=foto).update(Reconhecida=False)
                except:
                    messages.error(request, "não foi possivel setar false nas fotos ja reconhecidas")

        try:
            Recognition.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar todos reconhecimentos")

        try:
            Contador.objects.all().update(contador=0)
        except:
            messages.error(request, "não foi possivel zerar todos contadores")
    else:
        if utils.verifica_data(request, data):
            id = Dias.objects.get(data=data)
            if (Recognition.objects.filter(dias=id.id).count() > 0):
                var = Recognition.objects.filter(dias=id.id).values('foto_2')
                for i in var:
                    foto = i.get('foto_2')
                    if (Contador.objects.filter(foto_2_f=foto).count() > 0):
                        obj_cont = Contador.objects.get(foto_2_f=foto)
                        obj_cont.contador = F('contador') - 1
                        try:
                            obj_cont.save()
                        except:
                            messages.error(request, "não foi possivel zerar o cont de " + foto)

                var = Recognition.objects.filter(dias=id.id).values('foto_1')
                for i in var:
                    foto = i.get('foto_1')
                    try:
                        NovasFotos.objects.filter(novaimage=foto).update(Reconhecida=False)
                    except:
                        messages.error(request, "não foi possivel setar false nas fotos ja reconhecidas")

                try:
                    Recognition.objects.filter(dias=id.id).delete()
                except:
                    messages.error(request, "não foi possivel deletar" + data)




def get_info():
    tam_conhecidos = Recognition.objects.all().count()
    tam_desconhecidos = Vectors.objects.all().count()
    return  tam_conhecidos,tam_desconhecidos

def verifica_se_todos_processados(request,data):
    cont_true = NovasFotos.objects.filter(Reconhecida=True,fotos__dias__data=data).count()
    cont_false = NovasFotos.objects.filter(Reconhecida=False,fotos__dias__data=data).count()
    if cont_true > 0 and cont_false > 0:
        messages.error(request, "Existem fotos que não foram processadas em " + data+ ", logo dados inconsistentes")
