from django.contrib import admin

# Register your models here.
from Sistema.models import Fotos,NovasFotos,Intervalo

admin.site.register(Fotos)
admin.site.register(NovasFotos)
admin.site.register(Intervalo)