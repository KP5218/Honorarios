$(document).ready(function() {
    var correosSeleccionados = [];

    $('#rut').on('blur', function() {
        var rut = $(this).val().trim();
        if (rut.length > 0) {
            $.ajax({
                url: '/anular/filtrorut/' + encodeURIComponent(rut) + '/',
                method: 'POST',
                data: { rut: rut },
                success: function(data) {
                    var tbody = $('#results table tbody');
                    tbody.empty();

                    if (data.correos && data.correos.length > 0) {
                        $.each(data.correos, function(index, correo) {
                            var row = $('<tr>');
                            $('<td>').text(correo).appendTo(row);
                            var checkboxCell = $('<td>').appendTo(row);
                            var checkbox = $('<input>').attr('type', 'checkbox').appendTo(checkboxCell);

                            checkbox.on('change', function() {
                                if ($(this).is(':checked')) {
                                    correosSeleccionados.push({ "correo": correo, "checked": true, "rut": rut });
                                } else {
                                    correosSeleccionados = correosSeleccionados.filter(item => item.correo !== correo);
                                }
                                $('#correosSeleccionadosInput').val(JSON.stringify(correosSeleccionados));
                            });

                            row.appendTo(tbody);
                        });
                    } else {
                        tbody.append('<tr><td colspan="2">No se encontraron correos asociados.</td></tr>');
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        } else {
            $('#results table tbody').empty();
            correosSeleccionados = [];
        }
    });

    $('#form3').on('submit', function(event) {
        if (correosSeleccionados.length === 0) {
            event.preventDefault();
            alert('Debes seleccionar al menos un correo.');
        }
    });
});
