from django.urls import path
from . import views

app_name = 'Sistema'
urlpatterns = [
    path('', views.index, name='index'),
    #path('Sistema/Detec/', views.detec ,name = 'detec'),
    #path('Rec/', views.rec, name = 'rec')
    ##path ('Sistema/Conf/', views.gerar, name = 'gerar11')
]

