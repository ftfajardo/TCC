from .models import Fotos,NovasFotos,Dias,Intervalo
from django.conf import settings
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from . import views
import shutil
import re
from . import rec_utils


def get_dados(request):
    """ Método que pega os dados """
    data = str(request.POST.get('data'))
    interp = str( request.POST.get('form'))
    try:
        px = int(request.POST.get('px'))
    except:
        px = 70
    try:
        treshold = float(request.POST.get('threshold'))
    except:
        treshold = 0.7
    return data,px,treshold,interp



def gerar(request):
    """  Método que controla ações quando é clicado o botão de gerar faces """
    lista = []
    if request.method == 'POST':
        data,px,threshold,interp = get_dados(request)
        metodo = str(request.POST.get('form2'))

        if('check1' in request.POST):
            check_borda = True
        else:
            check_borda = False

        if ('check2' in request.POST):
            check_esca = True
        else:
            check_esca = False

        if ('check3' in request.POST):
            check_rota = True
        else:
            check_rota = False

        if ('check4' in request.POST):
            time = True
        else:
            time = False



        if data == "default":
            views.inserir_Fotos(request, lista,px,interp,threshold,check_borda,check_esca,check_rota,metodo,time)#insere todas as fotos
        else:
            if verifica_data(request, data):
                lista.append(data)
                views.inserir_Fotos(request,lista,px,interp,threshold,check_borda,check_esca,check_rota,metodo,time)  # insere todas as fotos de um dia
        return redirect('detec')
    else:
        return render(request, 'Conf/gerar.html', locals())


def excluir(request):
    """ Método que controla ações quando o botão de excluir é acionado """
    if request.method == 'POST':
        if 'executar' in request.POST:
            data = str(request.POST.get('data'))
            rec_utils.exclusao_total(request)
            if data == "default":
               delete_fotos_banco(request,1,data) #deleta todas fotos
            else:
                if verifica_data(request, data):
                    delete_fotos_banco(request,2,data) #deleta todas as fotos de um dia
            return redirect('detec')

    else:
        return render(request, 'Conf2/excluir.html')



def verifica_data(request,data):
    """  Método que verifica as propriedades de data inserida """
    controle = True
    if(len(data)!= 10):
        messages.error(request, "Data inválida deve ter 10 chars")
        controle = False

    pattern = r'(0?[1-9]|[12][0-9]|3[01])-(0?[1-9]|1[012])-((19|20)\d\d)'

    result = re.match(pattern, data)
    if not result:
        messages.error(request, "Data inválida")
        controle = False


    cont = 0
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for dir in dirs:
            if (str(dir) == data):
                cont = cont + 1
    if(cont == 0):
        messages.error(request, "data não existe no diretório")
        controle = False
    return  controle



def delete_fotos_banco(request,op,data):
    """
    #Método que deleta refêrencias do banco
    :param data : data para excluir
    :param op : controle de operacao
    """
    if(op == 1):    #deleta todas fotos
        lista_Datas =[]
        lista_Datas = os.listdir(settings.MEDIA_ROOT+'/dias/')


        try:
            Dias.objects.all().delete()
        except:
            messages.error(request, "não foi possivel deletar  dias")

        try:
            remove_log(op, data)
            for i in lista_Datas:
                path = settings.MEDIA_ROOT + "/dias/" + i + "/faces/"
                shutil.rmtree(path)  # removendo pasta das faces
        except:
            messages.error(request, "não existe fotos")

    else: #deleta fotos do dia
        try:
           Dias.objects.filter(data=data).delete()
        except:
            messages.error(request, "não foi possivel deletar"+data)

        path = settings.MEDIA_ROOT + "/dias/" + data + "/faces/"
        try:
            remove_log(op, data)
            if os.path.exists(path):
                shutil.rmtree(path)  # removendo pasta das faces
        except:
            messages.error(request, "não existe fotos")






def remove_log(op,data):
    #método que remove do log
    if(op !=1):
        with open(settings.BASE_DIR + "/log.txt", "r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if str(data) not in line:
                    f.write(line)
            f.truncate()
    else:
        os.remove(settings.BASE_DIR + "/log.txt")
        with open(settings.BASE_DIR + "/log.txt", "a+") as f:
            new_f = f.readlines()





def consistencia(request):
    validar(request,1)
    return redirect('detec')


def validar(request, op):
    """
    Método que verifica consistência a partir de um log
    """
    lista_datas = []
    # arquivo de log para consistência
    with open(settings.BASE_DIR + "/log.txt", "r+") as fileobj:
        for line in fileobj: #pega cada linha do arquivo
            if "inicio" in line:
                lista_datas.append(line[:8]) #insere na lista de datas com problema
            elif "fim" in line:
                lista_datas.remove(line[:8])  #remove da lista de datas com problemas
    if(len(lista_datas) != 0):
        #mensagem para ser printada na tela
        messages.error(request, " operacões inconsistentes refazer dia ou dias -- " + str(lista_datas))
    else:
        # mensagem para ser printada na tela
        messages.success(request, " operacões consistentes")

    if(op == 2): #tratando retorno da func do botao executar/gerar
        if(len(lista_datas) != 0):
            return False
        return True

def verifica_file(file,request):
    pattern = r'(\d\d):(\d\d):(\d\d)'
    result = re.match(pattern, file)
    if not result:
        messages.error(request, file + "com nome invalido, selecione checkbox de teste")
        return False
    return True



#connection
#('pq://hola:hola@postgres:5432/holadb')