document.addEventListener('DOMContentLoaded', function () {
    const cartIcon = document.getElementById('cart-icon');
    const cartSummary = document.getElementById('cart-summary');

    // Mostrar la ventanita cuando el mouse pasa sobre el ícono del carrito
    cartIcon.addEventListener('mouseenter', function() {
        cartSummary.style.display = 'block';
    });

    // Ocultar la ventanita cuando el mouse sale del ícono del carrito
    cartIcon.addEventListener('mouseleave', function() {
        cartSummary.style.display = 'none';
    });

    // Mostrar la ventanita si el mouse pasa sobre ella (dropdown)
    cartSummary.addEventListener('mouseenter', function() {
        cartSummary.style.display = 'block';
    });

    // Ocultar la ventanita si el mouse sale de la ventanita
    cartSummary.addEventListener('mouseleave', function() {
        cartSummary.style.display = 'none';
    });
});