import os
import pandas as pd
import requests, zipfile, io
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from pandas.api.types import is_object_dtype

class Command(BaseCommand):
    def handle(self, *args, **options):
        #podemos darle fechas que queramos
        today = datetime.now()
        excell_inicial = pd.DataFrame()
        excell_final = pd.DataFrame()
        # today = datetime(2023,7,1)
        for i in range(1, today.month):
            
            r = requests.get(
            f'https://transparenciachc.blob.core.windows.net/lic-da/{today.year}-{i}.zip')
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

            #hasta aqui es lo mismo
            file_path = f'data/lic_{today.year}-{i}.csv'
            #transformando los datos de la columna a lowercase, para mejorar el filtro
            df = pd.read_csv(file_path, sep = ";", encoding='latin-1', dtype='str')
            if df.empty:
                df.to_excel(f'./download/{i}-{today.year}.xlsx', index=False)
                self.stdout.write(
                    self.style.WARNING(
                            f"'ARCHIVO LEIDO VACIO "
                        )
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                            f"Se ha creado exitosamente'{i}-{today.year}.xlsx' "
                        )
                    )
                os.remove(file_path)
                continue

            # df = pd.read_csv('data/lic_2022-12.csv', encoding='latin-1')
            df['Nombre producto genrico'] = df['Nombre producto genrico'].apply(lambda x:x.upper()) 
            #filter = """`Nombre producto genrico` == 'CONSTRUCCIÓN DE CASAS'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE ACERAS, VEREDAS, CUNETAS'| `Nombre producto genrico` == 'CONSTRUCCIÓN DE EDIFICIOS Y DEPARTAMENTOS'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE LOCALES, PLANTAS COMERCIALES O INDUSTRIALES'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE MUROS DE CONTENCIÓN'|`Nombre producto genrico` == 'CONSTRUCCIÓN DE OBRAS CIVILES'"""
            #seleccionamos las columnas de interes 
            df2 = df[[
                'CodigoExterno',
                'Nombre',
                'Descripcion',
                'NombreOrganismo',
                'sector',
                'RutUnidad',
                'ComunaUnidad',
                'RegionUnidad',
                'FechaCreacion',
                'FechaCierre',
                'FechaAdjudicacion',
                'FechaEstimadaAdjudicacion',
                'MontoEstimado',
                'Rubro1',
                'Rubro2',
                'Nombre producto genrico',
                'RutProveedor',
                'NombreProveedor',
                'RazonSocialProveedor',
                'Monto Estimado Adjudicado',
                'MontoLineaAdjudica',
                'Oferta seleccionada']].copy()
            #tenemos que algunos campos deberian ser numericos
            if is_object_dtype( df2['MontoLineaAdjudica']):
                df2['MontoLineaAdjudica'] = df2['MontoLineaAdjudica'].str.replace(',','.')
            #if is_object_dtype( df2['CantidadAdjudicada']):
            #   df2['CantidadAdjudicada'] = df2['CantidadAdjudicada'].str.replace(',','.')
            if is_object_dtype( df2['MontoEstimado']):
                df2['MontoEstimado'] = df2['MontoEstimado'].str.replace(',','.')
            if is_object_dtype( df2['Monto Estimado Adjudicado']):
                df2['Monto Estimado Adjudicado'] = df2['Monto Estimado Adjudicado'].str.replace(',','.')
            
            df2['MontoLineaAdjudica'] = df2['MontoLineaAdjudica'].astype(float)
            #df2['CantidadAdjudicada'] = df2['CantidadAdjudicada'].astype(float)
            df2['MontoEstimado'] = df2['MontoEstimado'].astype(float)
            df2['Monto Estimado Adjudicado'] = df2['Monto Estimado Adjudicado'].astype(float)  

            #filtramos los datos de MontoLineaAdjudica >100.000.000 (precio de una casa)
            def filter_by_monto(row):
                return row['MontoLineaAdjudica'] > 100000000
            
            filtered_df2 = df2[df2.apply(filter_by_monto, axis=1)]
            #filtramos por nombres genericos
            filter_nombres = df['Nombre producto genrico'].isin(nombre_producto_generico)

            final_df = filtered_df2[filter_nombres]
            if not final_df.empty and  excell_inicial.empty:
                excell_inicial = final_df
                excell_inicial.to_excel(f'./download/{i}-{today.year}.xlsx', index=False)
                self.stdout.write(
                    self.style.SUCCESS(
                            f"Se ha creado exitosamente'{i}-{today.year}.xlsx' "
                        )
                    )
                os.remove(file_path)
                continue
            elif not final_df.empty and not excell_inicial.empty:
                excell_final = final_df
                comparacion = ~excell_final['CodigoExterno'].isin(excell_inicial['CodigoExterno'])
                excell_final = excell_final[comparacion]
                # Export the DataFrame to an Excel file
                excell_final.to_excel(f'./download/{i}-{today.year}.xlsx', index=False)
                self.stdout.write(
                    self.style.SUCCESS(
                            f"Se ha creado exitosamente'{i}-{today.year}.xlsx' "
                        )
                    )
                os.remove(file_path)
            elif final_df.empty:
                final_df.to_excel(f'./download/{i}-{today.year}.xlsx', index=False)
                self.stdout.write(
                    self.style.WARNING(
                            f"'{i}-{today.year}.xlsx' VACIO "
                        )
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                            f"Se ha creado exitosamente'{i}-{today.year}.xlsx' "
                        )
                    )
                os.remove(file_path)



