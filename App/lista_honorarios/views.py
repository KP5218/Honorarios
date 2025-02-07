import io

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa

from App.carga_datos.models import liqui_honorario_total, liqui_honorario_detalle


# Create your views here.
def busqueda_datos(criterio, valor):
    if criterio == "fecha_creacion":
        datos_totales = liqui_honorario_total.objects.filter(fecha_ingreso_datos=valor).values()
    elif criterio == "rut":
        datos_totales = liqui_honorario_total.objects.filter(rut=valor).values()
    elif criterio == "ambos":
        fecha_creacion, rut_medico = valor
        datos_totales = liqui_honorario_total.objects.filter(fecha_ingreso_datos=fecha_creacion, rut=rut_medico).values()
    elif criterio == "all":
        datos_totales = liqui_honorario_total.objects.all()
    else:
        raise ValueError("Criterio de búsqueda no válido")
    return datos_totales

def form_busqueda_datos(request):
    fecha_creacion = request.POST.get('fecha_creacion')
    rut_medico = request.POST.get('rut_medico')

    if request.method == 'POST':
        if fecha_creacion and rut_medico:
            criterio = "ambos"
            valor = (fecha_creacion, rut_medico)
        elif fecha_creacion:
            criterio = "fecha_creacion"
            valor = fecha_creacion
        elif rut_medico:
            criterio = "rut"
            valor = rut_medico
        else:
            criterio = "all"
            valor = "todo"

        try:
            datos_visualizacion = busqueda_datos(criterio, valor)
            messages.success(request, 'busqueda de datos realizada.')
        except ValueError:
            messages.error(request,'Criterio de búsqueda no válido.')

        if not datos_visualizacion:
            if criterio == "fecha_creacion":
                messages.error(request,'No se encontraron datos para la fecha especificada.')
            elif criterio == "rut":
                messages.error(request,'No se encontraron datos para el RUT especificado.')
            elif criterio == "ambos":
                messages.error(request,'No se encontraron datos para la fecha y el RUT especificados.')
            else:
                messages.error(request,'No se encontraron datos.')

        return render(request, 'lista_honorario/lista_honorario.html', {'datos_visualizacion': datos_visualizacion})

    return render(request, 'lista_honorario/lista_honorario.html')


def descargar_pdf(request):
    if request.method == 'POST':
        registro_seleccionado = request.POST.get('registro')

        if registro_seleccionado:
            rut, id_transaccion = registro_seleccionado.split(',')

            detalles_honorarios = liqui_honorario_detalle.objects.filter(rut=rut, id_transaccion=id_transaccion).order_by('fecha_creacion')
            total_liquidar = liqui_honorario_total.objects.filter(rut=rut, id_transaccion=id_transaccion).first()

            if detalles_honorarios and total_liquidar:
                resultado_total_liquidar_formato = "{:,}".format(total_liquidar.Total_liquidar)

                detalles_formateados = []

                for detalle in detalles_honorarios:
                    valor_formateado = "{:,}".format(detalle.total)
                    detalle_formateado = {
                        "fecha_creacion": detalle.fecha_creacion,
                        "op": detalle.op,
                        "nombre_paciente": detalle.nombre_paciente,
                        "prestacion": detalle.prestacion,
                        "valor": valor_formateado
                    }
                    detalles_formateados.append(detalle_formateado)


                context = {
                    "rut": rut,
                    "nombre": detalles_honorarios[0].nombre,
                    "fecha_periodo_desde": detalles_honorarios[0].fecha_periodo_desde,
                    "fecha_periodo_hasta": detalles_honorarios[0].fecha_periodo_hasta,
                    "periodo": detalles_honorarios[0].periodo,
                    "resultado_total_liquidar_formato": resultado_total_liquidar_formato,
                    "datos": detalles_formateados
                }

                template = get_template('pdf/pdf_honorario_imprimir.html')
                html = template.render(context)
                print(f"Buscando total_liquidar con rut={rut}, id_transaccion={id_transaccion}")

                pdf_file = io.BytesIO()
                pisa.CreatePDF(html, dest=pdf_file)

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{rut}.pdf"'
                response.write(pdf_file.getvalue())

                return response

    messages.error(request, "ocurrio un error")
    return redirect("form_busqueda_datos")