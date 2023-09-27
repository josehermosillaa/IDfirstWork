import os
import pandas as pd
import requests, zipfile, io
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import Cementera
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from pandas.api.types import is_object_dtype

class Command(BaseCommand):
    def handle(self, *args, **options):
        #podemos darle fechas que queramos
        # today = datetime.now()
        today = datetime(2023,7,1)
        r = requests.get(
        f'https://transparenciachc.blob.core.windows.net/lic-da/{today.year}-{today.month}.zip')
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./data")

        nombre_producto_generico = [
        'CONSTRUCCIÓN DE ACERAS, VEREDAS, CUNETAS',
        'CONSTRUCCIÓN DE CASAS',
        'CONSTRUCCIÓN DE EDIFICIOS Y DEPARTAMENTOS',
        'CONSTRUCCIÓN DE LOCALES, PLANTAS COMERCIALES O INDUSTRIALES',
        'CONSTRUCCIÓN DE MUROS DE CONTENCIÓN',
        'CONSTRUCCIÓN DE OBRAS CIVILES'
        ]
        file_path = f'data/lic_{today.year}-{today.month}.csv'
        #transformando los datos de la columna a lowercase, para mejorar el filtro
        df = pd.read_csv(file_path, sep = ";", lineterminator='\n', encoding='latin-1')
        # df = pd.read_csv('data/lic_2022-12.csv', encoding='latin-1')
        df['Nombre producto genrico'] = df['Nombre producto genrico'].apply(lambda x:x.upper()) 
        #filter = """`Nombre producto genrico` == 'CONSTRUCCIÓN DE CASAS'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE ACERAS, VEREDAS, CUNETAS'| `Nombre producto genrico` == 'CONSTRUCCIÓN DE EDIFICIOS Y DEPARTAMENTOS'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE LOCALES, PLANTAS COMERCIALES O INDUSTRIALES'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE MUROS DE CONTENCIÓN'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE OBRAS CIVILES'"""
        
        if is_object_dtype( df['MontoLineaAdjudica']):
            df['MontoLineaAdjudica'] = df['MontoLineaAdjudica'].str.replace(',','.')
        if is_object_dtype( df['CantidadAdjudicada']):
            df['CantidadAdjudicada'] = df['CantidadAdjudicada'].str.replace(',','.')
        suma_monto_linea = []
        cantidad_monto_linea = []
        suma_cantidad_adjudica = []
        for nombre in nombre_producto_generico:
            # print(nombre)
            df2 = df.query(f"`Nombre producto genrico` == '{nombre}'")[['Nombre producto genrico','MontoLineaAdjudica','CantidadAdjudicada']]
            
            #convertimos los datos str a float
            # df['MontoLineaAdjudica'] = df['MontoLineaAdjudica'].str.replace(',','.')
            # df['CantidadAdjudicada'] = df['CantidadAdjudicada'].str.replace(',','.')
            df2['MontoLineaAdjudica'] = df2['MontoLineaAdjudica'].astype(float)
            df2['CantidadAdjudicada'] = df2['CantidadAdjudicada'].astype(float)
            
            suma_monto_linea.append(df2['MontoLineaAdjudica'].sum())
            suma_cantidad_adjudica.append(df2['CantidadAdjudicada'].sum())
            cantidad_monto_linea.append(df2.query("`MontoLineaAdjudica`>0")['MontoLineaAdjudica'].count())
            # print(type(suma_monto_linea[0]))
            # print(type(suma_cantidad_adjudica[0]))
            try:
                Cementera.objects.create(
                    nombre=nombre, 
                    linea=suma_monto_linea[0].item(), 
                    cantidad=suma_cantidad_adjudica[0].item(), 
                    cuenta=int(cantidad_monto_linea[0].item()),
                    codigo_fecha=f'{today.month}-{today.year}',
                    monto_linea=suma_monto_linea[0].item(),
                    )
                suma_monto_linea = []
                cantidad_monto_linea = []
                suma_cantidad_adjudica = []
            except:
                self.stdout.write(self.style.ERROR('Datos ya cargados'))
        success = True
        self.stdout.write(
            self.style.SUCCESS(
                    "Se han cargado los datos correctamente"
                )
            )
        os.remove(file_path)
        if success:
            # data = Cementera.objects.filter(created__year=f'{today.year}',created__month=f'{today.month}')
            data = Cementera.objects.filter(codigo_fecha=f'{today.month}-{today.year}')
            context = {
                'data': data,
                'today':f'{today.day}/{today.month}/{today.year}'
                }

            subject = 'Correo de Prueba Cementeras'
            html_message = render_to_string('emails/cementera.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                ['pepe112@gmail.com']
            )
            
            email.attach_alternative(html_message, 'text/html')
            email.send()
            self.stdout.write(
            self.style.SUCCESS(
                    "Se ha enviado tu correo"
                )
            )