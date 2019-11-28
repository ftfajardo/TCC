
# Create your models here.
from django.db import models
from django.conf import settings



class Dias(models.Model):
    data = models.CharField(max_length=10, default='DEFAULT',null=False,unique=True)

class Metodo(models.Model):
    metodo = models.CharField(max_length=10, default='DEFAULT',null=False,unique=True)

class Intervalo(models.Model):
    inicio = models.IntegerField(default=-1,null=False)
    contador = models.IntegerField(null=True, blank=True, default=0)
    dia = models.ForeignKey(Dias,on_delete=models.CASCADE)
    metodo_f = models.ForeignKey(Metodo, on_delete=models.CASCADE)

    class Meta:
        ordering = ['inicio']

class Fotos(models.Model):
    image = models.ImageField('img', upload_to='media/',unique=True)
    dias = models.ForeignKey(Dias,on_delete=models.CASCADE)
    file_name = models.TextField(default='DEFAULT', null=False, unique=False)
    class Meta:
        ordering = ['file_name']

class NovasFotos(models.Model):
    novaimage = models.ImageField('img', upload_to='media/',unique=True)
    precisao = models.FloatField(null=True, blank=True, default=None)
    fotos = models.ForeignKey(Fotos, on_delete=models.CASCADE)
    metodo_f = models.ForeignKey(Metodo, on_delete=models.CASCADE)
    Reconhecida = models.BooleanField(default=False)


class Automatiza(models.Model):
    status = models.BooleanField(default=False)
    time =  models.TimeField(null=True, blank=True, default=None)


class Recognition(models.Model):
    foto_1 =  models.ImageField('img', upload_to='media/',unique=True)
    foto_2 = models.ImageField('img', upload_to='media/',unique=False)
    time = models.TimeField(null=True, blank=True, default=None)
    dias = models.ForeignKey(Dias,on_delete=models.CASCADE)
    metodo = models.CharField(max_length=10, default='DEFAULT', null=False, unique=False)
    distancia = models.FloatField(null=True, blank=True, default=None)
    distancia_real = models.FloatField(null=True, blank=True, default=None)

class Contador(models.Model):
    foto_2_f = models.ImageField('img', upload_to='media/', unique=False)
    contador = models.IntegerField(null=False, blank=False, default=0)


class Vectors(models.Model):
    file = models.TextField(default='DEFAULT', null=False, unique=True)
    vec_high = models.TextField(default='DEFAULT', null=False, unique=True)

class Distancias_reais(models.Model):
    distancia_real = models.FloatField(null=True, blank=True, default=None)
    foto_1 =  models.ImageField('img', upload_to='media/',unique=False)
    foto_2 = models.ImageField('img', upload_to='media/',unique=False)
