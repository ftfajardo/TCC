from .models import NovasFotos,Dias,Recognition,Contador,Vectors,Distancias_reais
from django.db import IntegrityError
from django.conf import settings
import os
from django.shortcuts import render, redirect
from django.contrib import messages
import cv2
import face_recognition
from . import utils
from . import rec_utils
from django.db.models import F
from django.db import transaction
import math

def PercorrendoImagens(request,lista_datas,distancia,metodo,inserir_desc_banco):
    """  Método que percorre os arquivos, procura match e insere informações no banco
     :param lista_datas: lista de datas para percorrer
     :param distancia: distancia desejada como máxima para duas fotos
     :param metodo: metodo a ser analisado
     :param inserir_desc_banco: controle de adição dos desconhecidos no banco
    """

    list(lista_datas)
    lista_erros =[]
    lista_acertos = []
    lista_acertos.append("Imagem nova inserida no banco: ")
    lista_erros.append("Imagem já foi processada antes ")

    #db = utils.connection()
    path = settings.MEDIA_ROOT+"/dias/"
    if len(lista_datas) == 0:
        lista_datas = os.listdir(path)

    for id in lista_datas:
        for root,dirs,files in os.walk(path + '/' + id + '/faces/'):
            for file in sorted(files):
                if(metodo in file):
                    path_imagem = path  + id+ '/faces/' + file
                    caminho_atual = "/media/dias/" + id + "/" + "faces/" + file
                    image = cv2.imread(path_imagem)
                    height,width,channels = image.shape
                    tuple = (0,0+width,0+height,0)
                    encodings = face_recognition.face_encodings(image,[tuple])
                    foto = NovasFotos.objects.get(novaimage=caminho_atual)
                    if len(encodings) > 0:
                        query_e = []
                        vetor_soma =[]
                        lista_objetos_distancias = []
                        if(Vectors.objects.all().count()>0):
                            ##distancia euclidiana sendo calculada
                            result = Vectors.objects.filter(file__contains=metodo).values()
                            for i in result:
                                vec_high = i.get('vec_high').split(",")
                                file_atual = i.get('file')
                                sub = []
                                j = []
                                for item in vec_high:
                                    j.append(float(item))


                                for h in range(0,128):
                                    sub.append((encodings[0][h]-j[h])*(encodings[0][h]-j[h]))

                                value = sum(sub)
                                sqrt = math.sqrt(value)
                                if(distancia > sqrt):
                                    if(len(vetor_soma) == 0):
                                        vetor_soma.append(sqrt)
                                        query_e.append(file_atual)
                                    elif(vetor_soma[0] > sqrt):
                                        query_e = []
                                        vetor_soma.append(sqrt)
                                        query_e.append(file_atual)
                                else:
                                    lista_objetos_distancias.append(Distancias_reais(foto_1=caminho_atual,foto_2=file_atual,distancia_real=sqrt))
                        if(len(query_e) == 0 and foto.Reconhecida==False and inserir_desc_banco == True):

                            query = Vectors(file=caminho_atual,vec_high=(','.join(str(s) for s in encodings[0][0:128])))
                            C = Contador(foto_2_f=caminho_atual)
                            foto = NovasFotos.objects.get(novaimage=caminho_atual)
                            foto.Reconhecida = True

                            try:
                                with transaction.atomic():
                                    foto.save()
                                    C.save()
                                    query.save()
                                    Distancias_reais.objects.bulk_create(lista_objetos_distancias)
                            except IntegrityError:
                                messages.error(request, "erro ao processar  " + caminho_atual)

                        elif len(query_e) > 0 and foto.Reconhecida == False :
                            caminho_banco = query_e[0]
                            hora = file[:8]
                            if (not caminho_banco == caminho_atual):
                                #soma um no contador
                                profile = Contador.objects.get(foto_2_f=caminho_banco)
                                profile.contador = F('contador') + 1


                                #salva os dados de reconhecimento
                                dia = Dias.objects.get(data=id)
                                R = Recognition(dias=dia,foto_1=caminho_atual  ,foto_2 =caminho_banco , time = hora,metodo = metodo,distancia = distancia,
                                                distancia_real=math.ceil(vetor_soma[0]*100)/100)

                                #marca foto como reconhecida
                                foto = NovasFotos.objects.get(novaimage=caminho_atual)
                                foto.Reconhecida = True

                                try:
                                    with transaction.atomic():
                                        R.save()
                                        profile.save()
                                        foto.save()

                                except IntegrityError:
                                    messages.error(request, "erro ao processar  "+ caminho_atual)


                                lista_acertos.append(" " +caminho_atual + " ")
                            else:
                                lista_erros.append(" " +caminho_atual + " "  )

                        elif(foto.Reconhecida == True ):
                            messages.error(request,path_imagem + " não encontrou vetores para descrever a face")

        rec_utils.verifica_se_todos_processados(request,id)


    if(len(lista_erros)>0):
        return lista_erros,lista_acertos





def rec_desconhecido(request):
    """  Método que faz o query de pessoas desconhecidas """
    query = Vectors.objects.all().values('file')
    i=[]
    for j in query:
        i.append(j.get('file'))
    lista_banco = []
    for image in i:
        n = image
        lista_banco.append(n)

    fotos  = NovasFotos.objects.filter(novaimage__in=lista_banco)
    fotos_cont = Contador.objects.all()
    return render(request, 'Rec/desconhecidos.html', {'fotos': fotos, 'lista_banco':lista_banco ,'fotos_cont':fotos_cont})












def rec(request):
    """  Método de controle para o reconhecimento """
    erro_tam = 0
    if request.method == 'POST':
        if 'botao' in request.POST:
            lista = []
            try:
                distancia = float(request.POST.get('dist'))

            except:
                distancia = 0.6

            data = str(request.POST.get('data'))
            if ('check1' in request.POST):
                inserir_desc_banco = True
            else:
                inserir_desc_banco = False
            metodo = str(request.POST.get('form2'))
            if data == "default":
               erros,acertos =  PercorrendoImagens(request,lista,distancia,metodo,inserir_desc_banco)
               erro_tam = len(erros)-1
            else:
                if utils.verifica_data(request, data):
                    lista.append(data)
                    erros, acertos =PercorrendoImagens(request,lista,distancia,metodo,inserir_desc_banco)
                    erro_tam = len(erros) - 1
    datas = Dias.objects.all()

    tam_conhecidos,tam_desconhecidos = rec_utils.get_info()

    return render(request, 'Rec/rec.html',locals())



def rec_gerar(request):
    return render(request, 'Rec/gerar_rec.html', locals())

def rec_excluir(request):
    return render(request, 'Rec/exc_gerar.html', locals())


def desconhecidos_distancias(request,file):
    obj = NovasFotos.objects.get(id=file)
    Distancias = Distancias_reais.objects.filter(foto_1=obj.novaimage)
    return render(request, 'Rec/desc_distancias.html', locals())

