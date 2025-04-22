from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Producto, Categoria, Pedido, ItemPedido
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm
from django.contrib import messages
from .models import Carrito, ItemCarrito

def index(request):
    categorias = Categoria.objects.all()
    productos_oferta = Producto.objects.filter(en_oferta=True)
    productos = Producto.objects.all()
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/index.html', {
        'categorias': categorias,
        'productos_oferta': productos_oferta,
        'productos': productos,
        'total_carrito': total_carrito
    })

def categorias(request):
    categorias = Categoria.objects.all()
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/categorias.html', {
        'categorias': categorias,
        'total_carrito': total_carrito
    })

def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/categorias.html', {
        'categoria': categoria,
        'categorias': categorias,
        'productos': productos,
        'total_carrito': total_carrito
    })

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()  # Crear el usuario
            login(request, usuario)  # Iniciar sesión automáticamente
            return redirect('productos:index')  # Redirigir al índice después de registrarse
    else:
        form = RegistroUsuarioForm()  # Crear un formulario vacío si es GET

    return render(request, 'productos/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('productos:index')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')  
            return render(request, 'productos/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'productos/login.html', {'form': form})



@login_required
def perfil_usuario(request):
    usuario = request.user
    pedidos = Pedido.objects.filter(usuario=usuario)

    # Obtener total de productos en el carrito desde la sesión
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/perfil.html', {
        'usuario': usuario,
        'pedidos': pedidos,
        'total_carrito': total_carrito
    })


def cerrar_sesion(request):
    logout(request)
    return redirect('productos:login')

def detalle_producto(request, id_producto):
    producto = Producto.objects.get(id=id_producto)
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/detalle.html', {
        'producto': producto,
        'total_carrito': total_carrito
    })

def buscar_productos(request):
    query = request.GET.get('search-input', '')
    productos = Producto.objects.filter(nombre__icontains=query)
    carrito = request.session.get('cart', {})
    total_carrito = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'productos/buscar.html', {
        'productos': productos,
        'query': query,
        'total_carrito': total_carrito
    })

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito_sesion = request.session.get('cart', {})
    producto_id_str = str(producto.id)

    if producto_id_str in carrito_sesion:
        carrito_sesion[producto_id_str]['cantidad'] += 1
    else:
        carrito_sesion[producto_id_str] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': 1,
            'imagen': producto.imagen.url if producto.imagen else ''
        }

    request.session['cart'] = carrito_sesion

    # Guardar en modelo
    if request.user.is_authenticated:
        carrito_obj, created = Carrito.objects.get_or_create(usuario=request.user)
        item, created = ItemCarrito.objects.get_or_create(carrito=carrito_obj, producto=producto)
        if not created:
            item.cantidad += 1
        item.save()

    return redirect(request.META.get('HTTP_REFERER', 'productos:index'))

def ver_carrito(request):
    carrito = request.session.get('cart', {})
    total = 0

    for id, item in carrito.items():
        subtotal = item['precio'] * item['cantidad']
        item['subtotal'] = subtotal
        total += subtotal

    total_carrito = sum(item['cantidad'] for item in carrito.values())

    context = {
        'carrito': carrito,
        'total': total,
        'total_carrito': total_carrito,
    }
    return render(request, 'productos/carrito.html', context)

def eliminar_del_carrito(request, producto_id):
    # Eliminar del carrito en la sesión
    carrito_sesion = request.session.get('cart', {})
    producto_id_str = str(producto_id)

    if producto_id_str in carrito_sesion:
        del carrito_sesion[producto_id_str]
        request.session['cart'] = carrito_sesion

    # Eliminar del carrito en la base de datos si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            carrito_obj = Carrito.objects.get(usuario=request.user)
            item_carrito = ItemCarrito.objects.get(carrito=carrito_obj, producto_id=producto_id)
            item_carrito.delete()  # Eliminar el item del carrito en la base de datos
        except ItemCarrito.DoesNotExist:
            pass  # Si el item no existe, no hacemos nada

    return redirect(request.META.get('HTTP_REFERER', 'productos:carrito'))

def modificar_cantidad_carrito(request, producto_id):
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        carrito = request.session.get('cart', {})
        producto_id_str = str(producto_id)

        if producto_id_str in carrito:
            if nueva_cantidad > 0:
                carrito[producto_id_str]['cantidad'] = nueva_cantidad
            else:
                del carrito[producto_id_str]

        request.session['cart'] = carrito

    return redirect('productos:carrito')

def vaciar_carrito(request):
    # Vaciar el carrito de la sesión
    request.session['cart'] = {}  
    request.session.modified = True

    # Vaciar el carrito en la base de datos si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            carrito_obj = Carrito.objects.get(usuario=request.user)
            # Eliminar todos los items en el carrito de la base de datos
            carrito_obj.items.all().delete()  # Borra todos los registros de ItemCarrito relacionados con el carrito
        except Carrito.DoesNotExist:
            pass  # Si no existe un carrito para el usuario, no hacemos nada

    return redirect('productos:carrito')


def compra_exitosa(request):
    carrito = request.session.get('cart', {})
    if not carrito:
        return redirect('productos:index')

    total = 0
    pedido = Pedido.objects.create(usuario=request.user, total=0)

    # Crear los registros de los items en el pedido
    for producto_id, datos in carrito.items():
        nombre = datos['nombre']
        precio = float(datos['precio'])
        cantidad = int(datos['cantidad'])
        subtotal = precio * cantidad
        total += subtotal

        # Crear un registro de ItemPedido
        ItemPedido.objects.create(
            pedido=pedido,
            nombre_producto=nombre,
            cantidad=cantidad,
            precio_unitario=precio
        )

        # Eliminar el item del carrito en la base de datos si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                carrito_obj = Carrito.objects.get(usuario=request.user)
                item_carrito = ItemCarrito.objects.get(carrito=carrito_obj, producto_id=producto_id)
                item_carrito.delete()  # Eliminar el item del carrito en la base de datos
            except ItemCarrito.DoesNotExist:
                pass  # Si el item no existe, no hacemos nada

    # Guardar el total del pedido en la base de datos
    pedido.total = total
    pedido.save()

    # Vaciar el carrito en la sesión
    request.session['cart'] = {}
    request.session.modified = True

    # Renderizar la página de compra exitosa
    return render(request, 'productos/compra.html', {
        'pedido': pedido
    })


def productos_en_oferta(request):
    productos_oferta = Producto.objects.filter(en_oferta=True)
    return render(request, 'productos/oferta.html', {
        'productos_oferta': productos_oferta
    })
