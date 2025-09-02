document.getElementById('form-tramite').addEventListener('submit', function (event) {
    event.preventDefault();

    // Mostrar el mensaje de éxito
    var successMessage = document.createElement('div');
    successMessage.classList.add('success-message');
    successMessage.innerText = '¡Gracias por enviar tu solicitud! Te responderemos lo más pronto posible.';
    
    // Agregar el mensaje al cuerpo de la página
    document.body.appendChild(successMessage);

    // Desvanecer el mensaje después de 3 segundos
    setTimeout(function() {
        successMessage.style.opacity = 0;
        setTimeout(function() {
            successMessage.remove(); // Eliminar el mensaje después de que desaparezca
        }, 500);
    }, 3000);

    // Reiniciar el formulario
    document.getElementById('form-tramite').reset();
});
