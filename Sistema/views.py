from .models import Fotos,NovasFotos,Dias,Intervalo,Metodo
from django.conf import settings
from django.db.models import F, Sum,Count
import os
from django.shortcuts import render, redirect
from django.contrib import messages
import cv2
from mtcnn.mtcnn import MTCNN
from .detec import Detec
from . import utils
import face_recognition


def index(request):
    return render(request, 'Sistema/index.html')

def detec_faces(request, Detec_obj):
    """
    Método de detecção que controla qual método foi escolhido e chama a classe para realizar operações
    :param Detec_obj: representa a classe que faz a detecção e tem os atributos
    """
    result,imagem = escolhe_metodo(Detec_obj)
   #passar o results na forma correta para o programa
    Detec_obj.detec_objs(request,imagem,result)

def escolhe_metodo(Detec_obj):
    """
       Método onde é realizado a escolha do método a ser utilizado e cria o dicionário do result,
       que torna possivel chamar a detecção para diferentes métodos.

       :param Detec_obj: representa a classe que faz a detecção e tem os atributos
       """

    if Detec_obj.metodo == "MTCNN":
        detector = MTCNN(None, 20, [Detec_obj.threshold, Detec_obj.threshold, Detec_obj.threshold], 0.709)
        imagem = cv2.imread(Detec_obj.local_foto)  # lendo imagem
        # o opencv funciona com bgr na ordem das cores, idealmente mudar para a detecção
        imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        # pegando resultados de detecção da img
        result = detector.detect_faces(imagem)
    else:
        imagem = face_recognition.load_image_file(Detec_obj.local_foto)
        if(Detec_obj.metodo == "HOG"):
            result_p = face_recognition.face_locations(imagem, 1, "hog")
        else:
            result_p = face_recognition.face_locations(imagem, 1, "NN-dlib")

        result = []

        #Criando o dicionário dos results, mais informações ler extra.txt
        for i in result_p:
            dict = {}
            landmarks = face_recognition.face_landmarks(imagem, result_p, 'small')
            list_temp = []
            list_temp.append(i[3])
            list_temp.append(i[0])
            list_temp.append(i[1] - i[3])
            list_temp.append(i[2] - i[0])
            dict["box"] = list_temp
            dict2 = {}
            re = landmarks[0].get('right_eye')
            le = landmarks[0].get('left_eye')
            tupla_re = re[0]
            tupla_le = le[0]
            dict2["right_eye"] = tupla_re
            dict2["left_eye"] = tupla_le
            dict["confidence"] = -1
            dict["keypoints"] = dict2

            result.append(dict)


    return result,imagem




def inserir_Fotos(request,lista_Datas,px,interp,threshold,borda,escala,rot,metodo,time):
    """ Método que preenche o banco com os dados iniciais necessários e percorre as fotos """



    if(utils.validar(request,2) == True):#chama func de validacao
        list(lista_Datas)
        Detec_obj = Detec(interp,px,threshold,borda,escala,rot,metodo,time)
        profile, created = Metodo.objects.get_or_create(metodo=metodo)
        if len(lista_Datas) == 0:
            lista_Datas = os.listdir(settings.MEDIA_ROOT+'/dias/') #se não vier um dia ocorre a operação em todos
        for data in lista_Datas: #pegar todas as datas para percorrer os diretorios
            f = open(settings.BASE_DIR + "/log.txt", "a+")#arquivo de log para consistência
            f.write("==============================================\n" + data + "- inicio" + " \n")
            f.close()

            if not os.path.exists(settings.MEDIA_ROOT+"/dias/"+data+"/faces/"):
                os.makedirs(settings.MEDIA_ROOT+"/dias/"+data+"/faces/")  # criando pasta das faces


            profile, created = Dias.objects.get_or_create(data=data)
            if(created == True):
                messages.success(request, data + " data criada")
            for  root, dirs, files in os.walk(settings.MEDIA_ROOT+"/dias/"+data): #for que percorre os diretórios
                for file in sorted(files):# for dos arquivos
                    if ((file.endswith("jpg") or file.endswith("png") )and ( "face_" not in file)):
                        var = True
                        if(Detec_obj.time == False):
                            var = utils.verifica_file(file,request)
                        if(var == True):
                            path = os.path.join(root, file)
                            # salvar no banco
                            caminho = "/media/dias/"+data+'/'+file
                            Diass = Dias.objects.get(data=data)
                            profile, created = Fotos.objects.get_or_create(image=caminho, dias=Diass,file_name=file[:-4])
                            Detec_obj.update_data(file,settings.MEDIA_ROOT+"/dias/"+data+"/faces/",path,"/media/dias/"+data+'/'+file,data)
                            detec_faces(request,Detec_obj) #funcao de detec

            f = open(settings.BASE_DIR + "/log.txt", "a+")
            f.write(data + "- fim" + " \n")
            f.close()

def dados(request):
    """  Método que manda informações para a tela dos dados individuais """
    dias_values = Dias.objects.all()
    mtcnn_values = Intervalo.objects.filter(metodo_f__metodo="MTCNN")
    hog_values = Intervalo.objects.filter(metodo_f__metodo="HOG")
    dlib_values = Intervalo.objects.filter(metodo_f__metodo="NN-dlib")
    return render(request, 'Detec/dados.html',locals())

def count(request,Metodo,id):
    parents = Fotos.objects.filter(novasfotos__metodo_f__metodo=Metodo).annotate(c_count=Count('novasfotos'))
    num_fotos = Fotos.objects.all().count()
    contador_verdadeiros = 0
    contador_falsos_positivos = 0
    contador_falsos_negativos = 0
    n = id
    for p in parents:
        contador_verdadeiros = contador_verdadeiros + 1
        if (p.c_count > n):
            var = p.c_count - n
            contador_falsos_positivos = contador_falsos_positivos + var

    contador_falsos_negativos = num_fotos - contador_verdadeiros
    return render(request, 'Fotos/dados.html', locals())


def fotos(request,Metodo):
    """ Método que manda informações para a tela das fotos """
    values = Dias.objects.all()
    Metodo_values = NovasFotos.objects.filter(metodo_f__metodo=Metodo)

    return render(request, 'Fotos/table.html', locals())

def detec(request):
    """ Método que manda informações para a tela de detecção """
    result_mtcnn = Intervalo.objects.filter(metodo_f__metodo='MTCNN').values('inicio').order_by('inicio').annotate(detecs=Sum('contador'))
    total_mtcnn = sum(result_mtcnn)

    result_hog = Intervalo.objects.filter(metodo_f__metodo='HOG').values('inicio').order_by('inicio').annotate(
        detecs=Sum('contador'))
    total_hog = sum(result_hog)

    result_dlib = Intervalo.objects.filter(metodo_f__metodo='NN-dlib').values('inicio').order_by('inicio').annotate(
        detecs=Sum('contador'))
    total_dlib = sum(result_dlib)

    return render(request, 'Detec/detec.html',locals())
def sum(metodo):
    soma = 0
    for i in metodo:
        soma = i.get('detecs') + soma
    return soma



