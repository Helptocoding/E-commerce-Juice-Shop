# store/urls.py

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Páginas públicas
    path('', views.home, name='home'),
    path('productos/', views.product_list, name='product_list'),
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
    path('categoria/<int:category_id>/', views.category_products, name='category_products'),
    
    # Carrito y checkout
    path('carrito/', views.cart_view, name='cart'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/remover/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrito/actualizar/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orden/confirmacion/<uuid:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('carrito/test/', views.cart_test, name='cart_test'), #Prueba
    
    # Panel de administrador
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/login/', views.admin_login, name='admin_login'),
    path('panel/pedidos/', views.admin_orders, name='admin_orders'),
    path('panel/pedidos/<uuid:order_number>/', views.admin_order_detail, name='admin_order_detail'),
    path('panel/pedidos/actualizar/<uuid:order_number>/', views.admin_update_order, name='admin_update_order'),
    path('panel/estadisticas/', views.admin_statistics, name='admin_statistics'),
    path('panel/test/', views.admin_test, name='admin_test'), #Prueba 
    
    #API para actualizacion en tiempo real
    path('panel/api/order-counts/', views.api_order_counts, name='api_order_counts'),
]