
document.addEventListener("DOMContentLoaded", function () {
    var loginModal = document.getElementById("loginModal");

    loginModal.addEventListener("show.bs.modal", function () {
        history.pushState(null, "", "/login"); // Cambia la URL a /login
    });

    loginModal.addEventListener("hidden.bs.modal", function () {
        history.pushState(null, "", "/"); // Vuelve a la URL anterior al cerrar el modal
    });
});

