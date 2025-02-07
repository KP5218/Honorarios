import csv
import io
import os
import smtplib
import zipfile
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from lxml import builder
from pypdf import PdfMerger
from xhtml2pdf import pisa

from .models import liqui_honorario_total, liqui_honorario_detalle, correo, periodo_liqui

# Create your views here.
def inicio(request):
    return render(
        request,
        'carga_datos/carga_datos.html'
    )

def detectar_delimitador(archivo):
    contenido = archivo.read().decode('utf-8')
    respuesta = csv.Sniffer().sniff(contenido, delimiters=";,")
    return respuesta.delimiter

def _obtener_siguiente_id_transaccion():
    if liqui_honorario_total.objects.exists():
        ultimo_total = liqui_honorario_total.objects.latest('id_transaccion')
        return ultimo_total.id_transaccion + 1
    else:
        return 1

def visualizar_datos(calculo_id_transaccion):
    datos_totales = liqui_honorario_total.objects.filter(id_transaccion=calculo_id_transaccion).values()
    return datos_totales

def guardar_db(request, datos_totales, datos_detalle,periodo_base, fecha_desde, fecha_hasta):

        calculo_id_transaccion = _obtener_siguiente_id_transaccion()
        for datos_totales in datos_totales:
            datos_liqui_totales = liqui_honorario_total(
                id_transaccion=calculo_id_transaccion,
                rut=datos_totales['RUT'],
                nombre=datos_totales['MEDICO'],
                Valor_total=datos_totales['VALOR'],
                Descuento_total=datos_totales['DESCUENTO'],
                Total_liquidar=datos_totales['TOTAL']
            )
            datos_liqui_totales.save()

        for datos_detalle in datos_detalle:
            datos_liqui_detalles = liqui_honorario_detalle(
                id_transaccion = calculo_id_transaccion,
                rut = datos_detalle['RUT'],
                nombre = datos_detalle['MEDICO'],
                prestacion=datos_detalle['CENTRO_COSTO_DESCRIPCION'],
                op=datos_detalle['OP'],
                nombre_paciente=datos_detalle['PACIENTE'],
                fecha_creacion=datos_detalle['FECHA_CREACION'],
                fecha_pago=datos_detalle['FECHA_PAGO'],
                fecha_periodo_desde=fecha_desde,
                fecha_periodo_hasta=fecha_hasta,
                periodo=periodo_base,
                valor=datos_detalle['VALOR'],
                descuento=datos_detalle['DESCUENTO'],
                total=datos_detalle['TOTAL']
            )
            datos_liqui_detalles.save()
        datos_visualizacion = visualizar_datos(calculo_id_transaccion)
        return datos_visualizacion


def form_carga_datos(request):
    periodo_bd = periodo_liqui.objects.all()
    mostrar_boton = True
    if request.method == 'POST' and request.FILES.get('csv_file'):
        archivo = request.FILES['csv_file']

        periodo = request.POST.get('select_periodo')
        fecha_desde = request.POST.get('fecha_desde')
        fecha_hasta = request.POST.get('fecha_hasta')

        periodo_base = periodo_liqui.objects.get(cod_periodo = periodo)

        if archivo.name.endswith('.csv'):

            delimitador = detectar_delimitador(archivo)
            archivo.seek(0)

            df = pd.read_csv(archivo, delimiter=delimitador, dtype={})

        elif archivo.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(archivo)
        else:
            messages.error(request, 'el archivo no es un csv ni un excel')

        columnas_requeridas = ['RUT', 'MEDICO', 'CENTRO_COSTO_DESCRIPCION',
                                'PACIENTE', 'OP', 'FECHA_CREACION', 'FECHA_PAGO', 'VALOR', 'DESCUENTO', 'TOTAL']

        if not all(columna in df.columns for columna in columnas_requeridas):
            messages.error(request,'El archivo no contiene todas las columnas requeridas (RUT, MEDICO, CENTRO_COSTO_DESCRIPCION,'
                                   ' PACIENTE, OP, FECHA_CREACION, FECHA_PAGO, VALOR, DESCUENTO, TOTAL.')
            return render(request, 'carga_datos/carga_datos.html')

        df.dropna(subset=columnas_requeridas, inplace=True)

        df = df[columnas_requeridas]

        df['VALOR'] = df['VALOR'].astype(int)
        df['DESCUENTO'] = df['DESCUENTO'].astype(int)
        df['TOTAL'] = df['TOTAL'].astype(int)

        df_detalles = df.sort_values(by='RUT')
        df_totales = df.groupby(['RUT','MEDICO']).agg({'VALOR':'sum', 'DESCUENTO':'sum','TOTAL':'sum'}).reset_index()

        datos_detalles = df_detalles.to_dict('records')
        datos_totales = df_totales.to_dict('records')

        datos_visualizacion = guardar_db(request,datos_totales, datos_detalles,periodo_base, fecha_desde, fecha_hasta)

        mostrar_boton = False
        messages.success(request, 'datos se han guardado satisfactoriamente en la base de datos.')
        return render(request, 'carga_datos/carga_datos.html', {'datos_visualizacion': datos_visualizacion , 'mostrar_boton': mostrar_boton, 'periodo_bd': periodo_bd})

    return render(request, 'carga_datos/carga_datos.html', {'periodo_bd': periodo_bd, 'mostrar_boton': mostrar_boton})

def busqueda_datos(request):
    if request.method == 'POST' and 'registro_seleccionado' in request.POST:
        columnas = request.POST.getlist('registro_seleccionado')
        resultados_por_rut = {}
        resultados_total_por_rut  = {}
        for columna in columnas:
            rut, id_transaccion = columna.split(',', 1)
            rut = rut.strip()
            id_transaccion = id_transaccion.strip()

            try:
                resultado = liqui_honorario_detalle.objects.filter(rut = rut, id_transaccion = id_transaccion)

                if rut not in resultados_por_rut:
                    resultados_por_rut[rut] = []

                resultados_por_rut[rut].append(resultado)

            except liqui_honorario_detalle.DoesNotExist:
                messages.error(request, f"No se encontró el registro con Rut {rut} y Id transaccion {id_transaccion}.")
                pass
        zip_file = crear_pdfs(request,resultados_por_rut, id_transaccion)

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="honorarios.zip"'

        return response

    elif request.method == 'POST':
        messages.error(request, 'Por favor seleccione al menos una fila y adjunte un archivo.')
        return HttpResponseRedirect(reverse(request,'form_carga_datos'))
    return HttpResponseRedirect(reverse('form_carga_datos'))

def crear_pdfs(request,resultados_por_rut, id_transaccion):
    errores = []
    contexto = {}
    datos = []
    rut_medico = ""
    nombre_medico = ""

    carpeta_inicial = 'C:/Users/desarrollocat/Desktop/liqui honorarios/'

    fecha_actual = datetime.now()

    carpeta_anio = str(fecha_actual.year)
    carpeta_mes = fecha_actual.strftime('%m')
    carpeta_dia = fecha_actual.strftime('%d')

    pdfs = []
    try:


        for rut, resultados in resultados_por_rut.items():
            rut_medico = rut
            resultado_valores_totales = liqui_honorario_total.objects.filter(rut=rut,id_transaccion=id_transaccion).first()
            resultado_total_liquidar = resultado_valores_totales.Total_liquidar
            resultado_total_liquidar_formato = "{:,}".format(resultado_total_liquidar)
            correobd = correo.objects.filter(rut=rut_medico)

            for resultado in resultados:
                for item in resultado:

                    nombre_medico = item.nombre
                    fecha_periodo_desde = item.fecha_periodo_desde
                    fecha_periodo_hasta = item.fecha_periodo_hasta
                    periodo = item.periodo

                    valor_formateado = "{:,}".format(item.total)
                    registro = [{"nombre": item.nombre, "rut": item.rut, "fecha_creacion": item.fecha_creacion,
                                 "op": item.op, "nombre_paciente": item.nombre_paciente,
                                 "prestacion": item.prestacion, "valor": valor_formateado}]
                    datos.append(registro)


            contexto = {"datos": datos, "rut": rut_medico, "nombre": nombre_medico, "fecha_periodo_desde": fecha_periodo_desde, "fecha_periodo_hasta": fecha_periodo_hasta, "periodo": periodo, "resultado_total_liquidar_formato": resultado_total_liquidar_formato}
            template = get_template('pdf/pdf_honorario.html')
            html = template.render(contexto)
            pdf_file = io.BytesIO()
            pisa.CreatePDF(html, dest=pdf_file)

            pdf_file.seek(0)

            pdf_content = pdf_file.getvalue()
            nombre_archivo = f"{rut}.pdf"

            pdfs.append({
                "nombre_archivo": nombre_archivo ,
                "contenido": pdf_content
            })
            if correobd.exists():
                envio_correo(request, correobd, pdf_content, nombre_archivo)

    except Exception as e:
        messages.error(request, f"Ocurrio un error al crear pdfs: {e}")

    zip_file = io.BytesIO()
    with zipfile.ZipFile(zip_file, 'w') as zf:
        for pdf in pdfs:
            zf.writestr(pdf["nombre_archivo"], pdf["contenido"])

    return zip_file


def envio_correo(request, correobd, pdf_content, nombre_archivo):
    # Simulación del servidor SMTP
    smtp_server = "localhost"
    smtp_port = 1025

    mensaje = MIMEMultipart()
    mensaje["From"] = 'correa.kro@gmail.com'
    mensaje["To"] = correobd[0].correo
    mensaje["Subject"] = 'Adjunto de archivo'

    mensaje.attach(MIMEText("¡Hola! Adjunto un archivo para ti.", "plain"))

    archivo_mime = MIMEBase('application', 'octet-stream')
    archivo_mime.set_payload(pdf_content)
    encoders.encode_base64(archivo_mime)
    archivo_mime.add_header('Content-Disposition', f'attachment; filename={nombre_archivo}')
    mensaje.attach(archivo_mime)

    try:
        # Simulación de envío: imprimir en consola en lugar de enviar
        print("\n=== Simulación de Envío de Correo ===")
        print(f"De: {mensaje['From']}")
        print(f"Para: {mensaje['To']}")
        print(f"Asunto: {mensaje['Subject']}")
        print("Cuerpo: ¡Hola! Adjunto un archivo para ti.")
        print(f"Adjunto: {nombre_archivo}")
        print("=====================================\n")

        messages.success(request, "Envío de correos realizada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al simular el envío del correo: {e}")
        print("Fallo en la simulación")

    return True