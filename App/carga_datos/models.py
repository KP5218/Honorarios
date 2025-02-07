from django.db import models
from datetime import date, datetime
# Create your models here.

class periodo_liqui(models.Model):
    class Meta:
        db_table = 'periodo_liqui'
    cod_periodo = models.CharField(null=False, blank=False,max_length=20, verbose_name="Cod periodo", unique=True)
    periodo = models.CharField(null=False,blank=False, max_length=20,verbose_name="periodo")

class liqui_honorario_detalle(models.Model):
    class Meta:
        db_table = 'liqui_honorario_detalle'
    id_transaccion = models.IntegerField(blank=True, null=True, verbose_name="Id Transaccion")
    rut = models.CharField(blank=True, null=True, max_length=11, verbose_name="RUT")
    nombre = models.TextField(blank=True, null=True, max_length=200, verbose_name="Nombre")
    fecha_ingreso_datos = models.DateField(blank=True, null=True, default=date.today, verbose_name="Fecha Ingreso")
    prestacion = models.TextField(blank=True, null=True, verbose_name="prestacion")
    op = models.BigIntegerField(blank=True, null=True, verbose_name="OP")
    nombre_paciente = models.TextField(blank=True, null=True, verbose_name="nombre paciente")
    fecha_creacion = models.TextField(blank=True, null=True, verbose_name="fecha creacion")
    fecha_pago = models.TextField(blank=True, null=True, verbose_name="fecha pago")
    fecha_periodo_desde = models.DateField(blank=True, null=True, verbose_name="Fecha periodo desde")
    fecha_periodo_hasta = models.DateField(blank=True, null=True, verbose_name="Fecha periodo hasta")
    periodo = models.ForeignKey(periodo_liqui, on_delete=models.RESTRICT, null=True, blank=True, verbose_name="periodo", to_field="cod_periodo")
    valor = models.IntegerField(blank=True, null=True, verbose_name="Valor")
    descuento = models.IntegerField(blank=True, null=True, verbose_name="Descuento")
    total = models.IntegerField(blank=True, null=True, verbose_name="Total")

class liqui_honorario_total(models.Model):
    class Meta:
        db_table = 'liqui_honorario_total'
    id_transaccion = models.IntegerField(blank=True, null=True, verbose_name="Id Transaccion")
    rut = models.CharField(blank=True, null=True, max_length=11, verbose_name="RUT")
    nombre = models.TextField(blank=True, null=True, max_length=200, verbose_name="Nombre")
    fecha_ingreso_datos = models.DateField(blank=True, null=True, default=date.today, verbose_name="Fecha Ingreso")
    Valor_total = models.IntegerField(blank=True, null=True,  verbose_name="Valor_total")
    Descuento_total = models.IntegerField(blank=True, null=True, verbose_name="Descuento_total")
    Total_liquidar = models.IntegerField(blank=True, null=True, verbose_name="Total_liquidar")

class fechas_entrega_pago_boleta(models.Model):
    class Meta:
        db_table = 'fechas_entrega_pago_boleta'
    id_transaccion = models.IntegerField(blank=True, null=True, verbose_name="Id Transaccion")
    fecha_entrega = models.DateField(blank=True, null=True, verbose_name="Fecha entrega boleta")
    fecha_pago = models.DateField(blank=True, null=True, verbose_name="Fecha pago")
    comentario = models.TextField(blank=True, null=True, verbose_name="comentario")

class correo(models.Model):
    class Meta:
        db_table = 'correo'
    rut = models.CharField(blank=True, null=True, max_length=11, verbose_name="RUT")
    nombre = models.TextField(blank=True, null=True, max_length=200, verbose_name="Nombre")
    correo = models.CharField(max_length=150, blank=False, null=False, verbose_name="Correo")
    valido = models.BooleanField(default=True, verbose_name="valido")
    correo_secundario = models.BooleanField(default=False, verbose_name="Correo secundario")

class Anulado(models.Model):
    class Meta:
        db_table = "Anulado"
    motivo_anulacion = models.TextField(max_length=255, verbose_name="Motivo de Anulación")
    fecha_anulacion = models.DateTimeField(default=datetime.today, verbose_name="Fecha de Anulación")
    responsable = models.TextField(null=True, blank=True, max_length=50, verbose_name="Nombre responsable")
    correo_id = models.ForeignKey('correo', verbose_name="id", null=True, blank=True, on_delete=models.CASCADE, to_field="id")