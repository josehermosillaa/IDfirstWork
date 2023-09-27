from django.shortcuts import render, HttpResponse
from .forms import DateForm
from .models import Cementera
from datetime import datetime
# Create your views here.
def home(request):
    return HttpResponse('<h1>Hola Mundo</h1>')

def prueba(request):
    today = datetime.now()
    if request.method == 'POST':
        month = request.POST['month']
        year = request.POST['year']
        data = Cementera.objects.filter(codigo_fecha=f'{month}-{year}')
        context = {
        'data': data,
        'today':f'{month}/{year}',
        'form': DateForm()
        }
        return render(request, 'core/table_data.html', context)
    else:
    # data = Cementera.objects.filter(created__year=f'{today.year}',created__month=f'{today.month}')
        data = Cementera.objects.filter(codigo_fecha=f'{today.month}-{today.year}')
    
        context = {
            'data': data,
            'today':f'{today.day}/{today.month}/{today.year}',
            'form': DateForm()
        }
        return render(request, 'core/table_data.html', context)