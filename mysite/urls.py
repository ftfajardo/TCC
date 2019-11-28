"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from Sistema import views as sistema_views
from Sistema import rec as sistema_rec
from Sistema import automat as sistema_aut
from Sistema import utils as sistema_utils

from Sistema import rec_utils
from . import  settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', sistema_views.index, name='index'),
    path('Sistema/', include('Sistema.urls')),
    path('admin/', admin.site.urls),
    path('Sistema/Detec/', sistema_views.detec, name='detec'),
    path('Sistema/validar/', sistema_utils.consistencia, name='consistencia'),
    path('Sistema/Conf/', sistema_utils.gerar, name='gerar'),
    path('Sistema/Conf2/', sistema_utils.excluir, name='excluir'),
    path('Rec/',sistema_rec.rec, name = 'rec'),
    path('Rec/recognition', sistema_rec.rec_gerar, name='rec_gerar'),
    path('Rec/desconhecidos', sistema_rec.rec_desconhecido, name='rec_desconhecido'),
    path('Rec/desc_dados/<int:file>', sistema_rec.desconhecidos_distancias, name='desconhecido_distancias'),
    path('Rec/excluir', sistema_rec.rec_excluir, name='rec_excluir'),
    path('Rec/ex', rec_utils.exclusao, name='exclusao'),
    path('Sistema/Automat/', sistema_aut.aut, name='aut'),
    path('Sistema/Automat/status/', sistema_aut.status, name='status'),
    path('Sistema/Automat/hora/', sistema_aut.hora, name='hora'),
    path('Sistema/Detec/dados/',sistema_views.dados,name = 'dados'),
    path('Sistema/Detec/dados/<str:Metodo>', sistema_views.fotos, name='fotos'),
    path('Sistema/Detec/dados/<str:Metodo>/<int:id>', sistema_views.count, name='count'),

]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)