document.addEventListener("DOMContentLoaded", function () {
    const rutInput = document.getElementById("rut");
    const rutHiddenInput = document.getElementById("rut_sin_formato");

    rutInput.addEventListener("input", function () {
        let value = rutInput.value.replace(/\D/g, ""); // Elimina todo excepto números
        if (value.length > 1) {
            let body = value.slice(0, -1);
            let verifier = value.slice(-1);
            body = body.replace(/\B(?=(\d{3})+(?!\d))/g, "."); // Agrega puntos cada 3 dígitos
            rutInput.value = `${body}-${verifier}`;
        }
    });

    // Al enviar el formulario, elimina los puntos y guion
    document.querySelector("form").addEventListener("submit", function () {
        rutHiddenInput.value = rutInput.value.replace(/\./g, "").replace(/-/g, ""); // Quita puntos y guion
    });
});
