from .models import Fotos,NovasFotos,Dias,Intervalo,Metodo
import cv2
import math
import numpy as np
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import F
import datetime


class Detec:

    def __init__(self,interp,px,treshold,borda,escala,rot,metodo,time):
        self.interp = interp
        self.px = px
        self.rotateTrue = rot
        self.Interp = escala
        self.ExcluirBorda = borda
        self.threshold = treshold
        self.filename = ""
        self.path = ""
        self.local_foto = ""
        self.banco_imagem = ""
        self.data = ""
        self.metodo = metodo
        self.time = time

    def update_data(self,filename,path,local_foto,banco_imagem,data):
        self.filename = filename
        self.path = path
        self.local_foto = local_foto
        self.banco_imagem = banco_imagem
        self.data = data
        self.formato = filename[-4:]

    def detec_objs(self,request,img,result):
        """  Método que começa a detecção, e controla as detecções em bordas
            :param img: imagem analisada
            :param result: dados da imagem que vem da detecção
        """

        if self.ExcluirBorda == True:
            for i in range(0, len(result)):
                bounding_box = result[i]['box']
                keypoints = result[i]['keypoints']
                confidence = float(result[i]['confidence'])
                controle = False
                # remoção de faces na borda antes da rotação
                (h, w) = img.shape[:2]
                if(bounding_box[0]+bounding_box[2] > w):
                    controle = True
                for j in bounding_box:
                    if j < 0:
                        controle = True

                if controle == False:  # se tudo ok seguir operações
                   self.operacoes(request,bounding_box,keypoints,confidence,img,i)
        else:
            for i in range(0, len(result)):
                bounding_box = result[i]['box']
                keypoints = result[i]['keypoints']
                confidence = float(result[i]['confidence'])
                self.operacoes(request, bounding_box, keypoints, confidence, img,i)




    def rotate(self,img, angle):
        """ Método de rotação que utiliza a matrizes de rotação
            :param img: imagem a ser modificada
            :param angle: ângulo de rotação
            """
        (h, w) = img.shape[:2]
        # coordenadas do centro da imagem para rotação sobre o centro
        center = (w / 2, h / 2)
        scale = 1.0
        # matriz de rotação dado um centro, um ângulo e uma escala
        M = cv2.getRotationMatrix2D(center, angle, scale)
        # aplicação da rotação
        img = cv2.warpAffine(img, M, (w, h))
        return img, M

    def rotation_angulo(self,keypoints):
        """  Método que calcula angulo para rotacionar
            :param keypoints: posições de olhos detectadas
        """
        # pontos dos olhos
        le = keypoints.get('left_eye')
        re = keypoints.get('right_eye')
        # obtenção do vetor
        dY = re[1] - le[1]
        dX = re[0] - le[0]
        # calculo do ângulo com relação ao eixo x
        angle = math.degrees(math.atan2(dY, dX))
        # coloca o ângulo no mesmo sentido
        if (angle < 0):
            angle = 360 + angle
        return angle

    def interp_method(self,interp):
        """
        Método que pega a func de interp
        :param func de interp escolhida
        """

        if interp == "INTER_LINEAR":
            return cv2.INTER_LINEAR
        elif interp == "INTER_CUBIC":
            return cv2.INTER_CUBIC
        elif interp == "INTER_AREA":
            return cv2.INTER_AREA


    def verifica_existencia(self,string):
        """  Método que verifica se ja existe imagem com stirng de tempo
            :param string: string com o tempo
        """
        retorno = False
        all_novas_fotos = NovasFotos.objects.filter(fotos__dias__data=self.data).values('novaimage')
        for values in all_novas_fotos:
            value = values.get('novaimage')
            if(string in value):
                retorno = True
                break
        return retorno

    def operacoes(self,request,bounding_box,keypoints,confidence,img,i):
        """  Método que realiza as operações sobre a imagem e insere os dados no banco
            :param bounding_box: caixa da face que contem as coordenadas da mesma
            :param keypoints: coordenadas dos olhos
            :param confidence: confiança sobre uma detecção
            :param img: imagem analisada
            :param i: número da face detectada em uma imagem
        """
        erro_de_sistema = False
        erro = False
        altura = bounding_box[3]
        largura = bounding_box[2]
        # centro da bounding box
        p_central = (
            (bounding_box[0] + bounding_box[0] + largura) / 2, (bounding_box[1] + bounding_box[1] + altura) / 2)
        if (self.rotateTrue == True):

            # rotação
            angle = self.rotation_angulo(keypoints)
            img, M = self.rotate(img, angle)

            # conseguir o ponto rotacionado
            ponto_rotacionado = M.dot(np.array(p_central + (1,)))
            px = int(ponto_rotacionado[0])
            py = int(ponto_rotacionado[1])
        else:
            px = (bounding_box[0] + bounding_box[0] + largura) / 2
            py = (bounding_box[1] + bounding_box[1] + altura) / 2

        # recorte da figura
        img = img[round(py - (largura / 2)):round(py + (altura / 2)),
              round(px - (largura / 2)):round(px + (largura / 2))]

        if (self.Interp == True):
            # fazer escala px = 70,70
            try:
                imagemescalada = cv2.resize(img, (self.px, self.px),
                                            interpolation=self.interp_method(self.interp))
            except:
                messages.error(request,
                               " foto" + self.filename + " não pode ser inserida no banco, escalada")
                imagemescalada = img
        else:
            imagemescalada = img

        imagemescalada = cv2.cvtColor(imagemescalada, cv2.COLOR_RGB2BGR)

        #controle do nome do arquivo
        if(len(self.filename)> 12 and self.time == False):
            self.filename = self.filename[:8]

        elif(self.time == True):
            try:
                now = datetime.datetime.now()
                time = now.strftime("%H:%M:%S")
                self.filename = time
                controle = self.verifica_existencia(time)

                while(controle == True):
                    now = datetime.datetime.now()
                    time = now.strftime("%H:%M:%S")
                    self.filename = time
                    controle = self.verifica_existencia(time)



            except OSError:
                erro_de_sistema = True
                messages.error(request, "erro no SO para pegar tempo do arquivo")

        if(erro_de_sistema == False):
            caminho = "/media/dias/" + self.data + "/" + "faces/" + self.filename + "_face_" + str(
                i + 1) + "_" + self.data + "_" + self.metodo + "_" + self.formato

            # salva as imagens
            cv2.imwrite(self.path +self.filename + "_face_" + str(i + 1) + "_" + self.data + "_" + self.metodo + "_"+self.formato ,
                        imagemescalada)
            fotos = Fotos.objects.get(image=self.banco_imagem)
            metodo = Metodo.objects.get(metodo=self.metodo)


            N = NovasFotos(
                novaimage=caminho,
                precisao=format(confidence, '.4f'), fotos=fotos,metodo_f=metodo)

            try:
                N.save()
            except IntegrityError as e:
                #messages.error(request, " foto" + caminho + " já existe")
                erro = True

            # pega tempo e soma contador de detec das fotos
            if erro == False:
                modificationTime = int(self.filename[:2])
                Diass = Dias.objects.get(data=self.data)
                obj_fotos, criada = Intervalo.objects.get_or_create(dia=Diass, inicio=modificationTime, metodo_f = metodo)
                obj_fotos.contador = F('contador') + 1
                obj_fotos.save()


