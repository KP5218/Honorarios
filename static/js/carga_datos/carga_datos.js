//evento de subir el csv
document.getElementById('formulario_datos').addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        alert('Por favor, llene todos los campos requeridos.');
    } else {
        var respuesta = confirm("¿Estás seguro de que deseas cargar este archivo?, se guardará en la base de datos.");
        if (respuesta == true) {
            document.getElementsById('submit_button').click();
        } else {
            alert("No se cargó el archivo.");
            document.getElementById("csv_file").value = "";
            event.preventDefault();
        }
    }
});




//el evento del check
window.addEventListener('load', function() {
    let seleccionarTodoElement = document.getElementById('seleccionarTodo');
    if (seleccionarTodoElement) {
        seleccionarTodoElement.addEventListener('change', function() {
            let checkboxes = document.querySelectorAll('input[name="registro_seleccionado"]');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = seleccionarTodoElement.checked;
            });
        });
    }
});

function validarCheckbox() {
    var checkboxes = document.getElementsByName("registro_seleccionado");
    var alMenosUnoSeleccionado = false;
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            alMenosUnoSeleccionado = true;
            break;
        }
    }
    if (!alMenosUnoSeleccionado) {
        alert("Por favor, seleccione al menos un registro.");
        return false;
    }
    var campos_requeridos = document.querySelectorAll("#formulario [required]");
    var campos_validados = true;

    campos_requeridos.forEach(field => {
        if (!field.value.trim()){
            field.style.borderColor = "red";
            campos_validados = false;
        }else{
            field.style.borderColor = "";
        }
    });

    if(!campos_validados){
        alert("Por favor, complete los campos requeridos.");
        return false;
    }

    enviardatos();
    return true;
}

function enviardatos() {
    var formulario = document.getElementById('formulario');
    var tabla = document.getElementById('tablaDatos');

    formulario.submit();

    setTimeout(function () {
        tabla.innerHTML = '';

        alert('Los datos se han procesado correctamente.');


        window.location.href = 'http://127.0.0.1:8000/carga_datos/';


    }, 3000);
}