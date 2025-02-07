document.getElementById('boton_limpiar').addEventListener('click', function() {
    window.location.href = 'http://127.0.0.1:8000/lista_honorarios/';
});

// Asegurar que solo se pueda marcar un checkbox a la vez
const checkboxes = document.querySelectorAll('.registro-checkbox');
checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        checkboxes.forEach(cb => {
            if (cb !== this) {
                cb.checked = false;
            }
        });
    });
});