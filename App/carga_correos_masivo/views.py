import csv
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from itertools import cycle
import re
from django.db import IntegrityError
from App.carga_datos.models import correo
from django.db.models import Max


def detectar_delimitador(archivo):
    contenido = archivo.read().decode('utf-8')
    respuesta = csv.Sniffer().sniff(contenido, delimiters=";,")
    return respuesta.delimiter

def validar_correo_electronico(correo):
    regex = r"""^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"""
    if re.search(regex, correo):
        return True
    else:
        return False

def validarRut(rut):
    rut = rut.upper()
    rut = rut.replace("-", "")
    rut = rut.replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]

    revertido = map(int, reversed(str(aux)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(revertido, factors))
    res = (-s) % 11

    if str(res) == dv:
        return True
    elif dv == "K" and res == 10:
        return True
    else:
        return False

def guardar_correos(request, datos_correos):
    errores_validacion = []

    ultimo_id = correo.objects.aggregate(Max('id'))['id__max']
    nuevo_id = (ultimo_id + 1) if ultimo_id else 1

    for datos_correos in datos_correos:
        errores_registro = []
        datos_validos = {}

        try:
            rut = datos_correos['RUT'].strip()
            nombre = datos_correos['MEDICO'].strip()
            correo_excel = datos_correos['CORREO'].strip()
            valor_valido = datos_correos['VALIDO']
            valor_correo_secundario = datos_correos['CORREO_SECUNDARIO']

            if isinstance(valor_valido, bool):
                valido_validado = valor_valido
            elif valor_valido in ("True", "1", "si"):
                valido_validado = True
            elif valor_valido in ("False", "0", "no"):
                valido_validado = False
            elif valor_valido == "":
                valido_validado = False
            else:
                errores_registro.append(f"El valor 'VALIDO' para el RUT '{rut}' no es válido. Debe ser 'True', 'False', 'Si', 'No', '1' o '0'.")

            if isinstance(valor_correo_secundario, bool):
                correo_secundario_validado = valor_correo_secundario
            elif valor_correo_secundario in ("True", "1", "si"):
                correo_secundario_validado = True
            elif valor_correo_secundario in ("False", "0", "no"):
                correo_secundario_validado = False
            elif valor_correo_secundario == "":
                correo_secundario_validado = False
            else:
                errores_registro.append(f"El valor 'CORREO_SECUNDARIO' para el RUT '{rut}' no es válido. Debe ser 'True', 'False', 'Si', 'No', '1' o '0'.")


            if not validarRut(rut):
                errores_registro.append(f"El RUT '{rut}' no tiene un formato válido.")


            if not validar_correo_electronico(correo_excel):
                errores_registro.append(f"El correo electrónico '{correo_excel}' no tiene un formato válido.")


            if not errores_registro:
                datos_validos = {
                    "id": nuevo_id,
                    "rut": rut,
                    "nombre": nombre,
                    "correo": correo_excel,
                    "valido": valido_validado,
                    "correo_secundario": correo_secundario_validado,
                }
                nuevo_id += 1

        except Exception as e:
            errores_registro.append(f"Error inesperado: {str(e)}")

        if errores_registro:
            errores_validacion.append({"rut": rut, "errores": errores_registro})
            continue

        datos = correo.objects.create(**datos_validos)
        datos.save()

    if errores_validacion:
        mensajes_error = []

        for error in errores_validacion:
            rut = error["rut"]
            mensajes_error_rut = [f"RUT: {rut}"]
            mensajes_error_rut.extend(error["errores"])
            mensajes_error.append("\n".join(mensajes_error_rut))

        mensaje_unificado = "\n".join(mensajes_error)
        messages.error(request, mensaje_unificado)

    return True

def form_carga_correos(request):
    if request.method == 'POST' and request.FILES.get('csv_file_correos'):
        archivo = request.FILES['csv_file_correos']

        if archivo.name.endswith('.csv'):
            delimitador = detectar_delimitador(archivo)
            archivo.seek(0)

            df = pd.read_csv(archivo, delimiter=delimitador)

        elif archivo.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(archivo)
        else:
            messages.error(request, 'El archivo no es un CSV ni un Excel')

        columnas_requeridas = ['RUT', 'MEDICO', 'CORREO', 'VALIDO', 'CORREO_SECUNDARIO']

        if not all(columna in df.columns for columna in columnas_requeridas):
            messages.error(request, 'El archivo no contiene todas las columnas requeridas (RUT, MEDICO, CORREO, VALIDO, CORREO_SECUNDARIO)')
            return render(request, 'carga_correos_masivo/carga_correo_masivo.html')

        df.dropna(subset=columnas_requeridas, inplace=True)

        df = df[columnas_requeridas]

        df_correos = df.sort_values(by='RUT')

        datos_correos = df_correos.to_dict('records')

        datos_guardados = guardar_correos(request, datos_correos)

        if datos_guardados:
            messages.success(request, 'Los datos se han guardado satisfactoriamente en la base de datos...')
            return render(request, 'carga_correos_masivo/carga_correo_masivo.html')

    return render(request, 'carga_correos_masivo/carga_correo_masivo.html')