from .models import Automatiza
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages




def aut(request):
    obj = Automatiza.objects.all()
    if not obj:
        N = Automatiza(status= False, time='17:00')
        try:
            N.save()
        except IntegrityError as e:
            messages.error(request, "não pode ser inserida no banco")

    obj = Automatiza.objects.all()
    return render(request, 'Automat/auto.html',locals())



def status(request):
    obj = Automatiza.objects.all().first()
    if obj.status == False :
        obj.status = True
        #print(obj.status)
    else:
        obj.status = False
    try:
        obj.save()
    except IntegrityError as e:
        messages.error(obj.status + "não pode ser inserida no banco")

    return redirect('aut')


def hora(request):
    if request.method == 'POST':
        if 'hora' in request.POST:
            try:
                data = str(request.POST.get('hora'))
            except:
                messages.error(request, "string error")
                return render(request, 'Automat/auto.html', locals())

            obj = Automatiza.objects.all().first()
            obj.time =data
            try:
                obj.save()
            except IntegrityError as e:
                messages.error(request, data +  " não pode ser inserida no banco")

    return redirect('aut')
