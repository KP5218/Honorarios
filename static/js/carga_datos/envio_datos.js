// Función para manejar la descarga del archivo ZIP y limpiar la página
function descargarYLimpiarPagina() {
    const registrosSeleccionados = [];

    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        const valor = checkbox.value;

    if (valor !== "") {
        registrosSeleccionados.push(valor);
    }
    });

    fetch('/carga_datos/busqueda_datos/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'registros_seleccionados': registrosSeleccionados })
    })
    .then(response => {
        if (response.ok) {
            return response.blob().then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'honorarios.zip';
                document.body.appendChild(a);
                a.click();
                a.remove();

                limpiarPagina();
            });
        } else {
            throw new Error('Error al descargar el archivo ZIP');
        }
    })
    .catch(error => {
        console.error('Error en la solicitud AJAX:', error);
    });
}
function limpiarPagina() {
        setTimeout(() => {
            window.location.href = 'http://127.0.0.1:8000/carga_datos/';
        }, 2000);
    }


    // Función para obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}