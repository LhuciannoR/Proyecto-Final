from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('categorias/', views.categorias, name='categorias'),
    path('productos/categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('detalle/<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('ofertas/', views.productos_en_oferta, name='productos_en_oferta'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Carrito
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/modificar/<int:producto_id>/', views.modificar_cantidad_carrito, name='modificar_cantidad_carrito'),
    path('vaciar-carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
]
