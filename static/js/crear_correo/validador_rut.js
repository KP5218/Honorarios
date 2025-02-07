//---------VALIDADOR DE RUT------------------->
let alerta = document.getElementById("alerta");
let mensaje = document.getElementById("mensaje");
let botonguardar = document.getElementById("crear");
function isNumber(evt) {
  let charCode = evt.which;

  if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode === 75) {
    return false;
  }

  return true;
}

function checkRut(rut) {
  if (rut.value.length <= 1) {
    alerta.classList.remove('alert-success', 'alert-danger');
    alerta.classList.add('alert-info');
    mensaje.innerHTML = 'Debe ingresar un Rut';
    botonguardar.disabled = true;
  }

  let valor = clean(rut.value);

  let bodyRut = valor.slice(0, -1);
  let dv = valor.slice(-1).toUpperCase();

  rut.value = format(rut.value);

  if (bodyRut.length < 7) {
    alerta.classList.remove('alert-success', 'alert-danger');
    alerta.classList.add('alert-info');
    mensaje.innerHTML = 'Ingresó un RUT muy corto';
    botonguardar.disabled = true;
    return false;
  }

  suma = 0;
  multiplo = 2;

  for (i = 1; i <= bodyRut.length; i++) {
    index = multiplo * valor.charAt(bodyRut.length - i);

    suma = suma + index;

    if (multiplo < 7) {
      multiplo = multiplo + 1;
    } else {
      multiplo = 2;
    }
  }

  dvEsperado = 11 - (suma % 11);

  dv = dv == "K" ? 10 : dv;
  dv = dv == 0 ? 11 : dv;

  if (dvEsperado != dv) {
    alerta.classList.remove('alert-info', 'alert-success');
    alerta.classList.add('alert-danger');
    mensaje.innerHTML = 'El RUT ingresado: ' + rut.value + ' Es <strong>Invalido</strong>.';
    botonguardar.disabled = true;

    return false;
  } else {
    alerta.classList.remove('d-none', 'alert-danger');
    alerta.classList.add('alert-success');
    mensaje.innerHTML = '';
    botonguardar.disabled = false;
    }
}
function format(rut) {
  rut = clean(rut)

  var result = rut.slice(-4, -1) + '-' + rut.substr(rut.length - 1)
  for (var i = 4; i < rut.length; i += 3) {
    result = rut.slice(-3 - i, -i) + '' + result
  }

  return result;
}

function clean (rut) {
  return typeof rut === 'string'
    ? rut.replace(/^0+|[^0-9kK]+/g, '').toUpperCase()
    : ''
}