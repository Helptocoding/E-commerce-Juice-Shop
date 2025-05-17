# store/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.auth import authenticate, login
from .models import Category, Product, Order, OrderItem
from .forms import CheckoutForm, AdminLoginForm, OrderUpdateForm
import json
import uuid
from datetime import timedelta

# Función auxiliar para verificar si un usuario es administrador
def is_admin(user):
    return user.is_superuser or user.is_staff

# Vistas públicas
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(available=True)[:6]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/products.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, available=True)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_products.html', context)

# Funciones del carrito
def get_cart_from_session(request):
    cart = request.session.get('cart', {})
    return cart

# Actualizar la vista cart_view para incluir la funcionalidad de vaciar el carrito

def cart_view(request):
    """
    Vista para mostrar el contenido del carrito y permitir manipularlo.
    """
    # Comprobar si se está vaciando el carrito
    if request.method == 'POST' and 'clear_cart' in request.POST:
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, "El carrito ha sido vaciado correctamente.")
        return redirect('store:cart')
    
    # Obtener el carrito de la sesión
    cart = get_cart_from_session(request)
    cart_items = []
    total = 0
    
    print(f"Debug - Contenido del carrito en cart_view: {cart}")
    
    # Procesar los ítems del carrito
    for product_id, item_data in cart.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            quantity = item_data.get('quantity', 1)
            subtotal = product.price * quantity
            total += subtotal
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
            print(f"Debug - Producto en vista cart: {product.name}, cantidad: {quantity}, subtotal: {subtotal}")
        except Product.DoesNotExist:
            print(f"Debug - Producto no encontrado: {product_id}")
            # Eliminar productos que ya no existen
            cart.pop(product_id, None)
            request.session['cart'] = cart
            request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

# Actualizar la función add_to_cart en store/views.py con mejores manejo de AJAX

def add_to_cart(request, product_id):
    """
    Añade un producto al carrito de compras.
    Soporta peticiones AJAX y normales.
    """
    # Verificar si es una petición AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Convertir product_id a string para uso en diccionario de carrito
        product_id_str = str(product_id)
        product = get_object_or_404(Product, id=product_id)
        cart = get_cart_from_session(request)
        
        print(f"Debug - Carrito antes de agregar: {cart}")
        
        # Obtener cantidad desde el formulario
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
        
        print(f"Debug - Agregando producto {product.name} (ID: {product_id_str}), cantidad: {quantity}")
        
        # Actualizar o añadir al carrito
        if product_id_str in cart:
            # Si el producto ya está en el carrito, aumentar cantidad
            cart[product_id_str]['quantity'] += quantity
            print(f"Debug - Producto ya en carrito, nueva cantidad: {cart[product_id_str]['quantity']}")
        else:
            # Si es nuevo, añadir con estructura consistente
            cart[product_id_str] = {'quantity': quantity}
            print(f"Debug - Nuevo producto en carrito: {cart[product_id_str]}")
        
        # Guardar carrito en la sesión y marcar como modificado
        request.session['cart'] = cart
        request.session.modified = True
        
        print(f"Debug - Carrito después de agregar: {cart}")
        
        # Calcular el total de items en el carrito
        cart_count = sum(item['quantity'] for item in cart.values())
        print(f"Debug - Total de items en carrito: {cart_count}")
        
        # Mostrar mensaje de éxito (solo para peticiones no-AJAX)
        if not is_ajax:
            messages.success(request, f"{product.name} agregado al carrito!")
        
        # Si es una petición AJAX, devolver JSON
        if is_ajax:
            return JsonResponse({
                'success': True, 
                'cart_count': cart_count,
                'message': f"{product.name} agregado al carrito!",
                'product_name': product.name,
                'quantity': quantity,
                'cart': cart  # Para depuración
            })
        
        # Si no es AJAX, redirigir de vuelta a la página anterior
        referer_url = request.META.get('HTTP_REFERER')
        if referer_url:
            return redirect(referer_url)
        else:
            # Si no hay referrer, redirigir a la lista de productos
            return redirect('store:product_list')
            
    except Exception as e:
        print(f"Error en add_to_cart: {e}")
        # Manejar cualquier error
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        # Si no es AJAX, mostrar mensaje de error y redirigir
        messages.error(request, "No se pudo agregar el producto al carrito.")
        return redirect('store:product_list')

def remove_from_cart(request, product_id):
    cart = get_cart_from_session(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': sum(item['quantity'] for item in cart.values())})
    
    return redirect('store:cart')

def update_cart(request, product_id):
    """
    Actualiza la cantidad de un producto en el carrito.
    """
    # Convertir product_id a string para uso en diccionario de carrito
    product_id_str = str(product_id)
    cart = get_cart_from_session(request)
    
    print(f"Debug - Carrito antes de actualizar: {cart}")
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    print(f"Debug - Actualizando producto ID: {product_id_str}, nueva cantidad: {quantity}")
    
    if product_id_str in cart:
        if quantity > 0:
            # Actualizar cantidad
            cart[product_id_str]['quantity'] = quantity
            print(f"Debug - Cantidad actualizada: {cart[product_id_str]}")
        else:
            # Eliminar producto si cantidad es 0 o menor
            del cart[product_id_str]
            print(f"Debug - Producto eliminado del carrito")
    
    # Guardar carrito en la sesión y marcar como modificado
    request.session['cart'] = cart
    request.session.modified = True
    
    print(f"Debug - Carrito después de actualizar: {cart}")
    
    # Si es una petición AJAX, devolver respuesta JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = sum(item['quantity'] for item in cart.values())
        return JsonResponse({
            'success': True, 
            'cart_count': cart_count,
            'cart': cart  # Para depuración
        })
    
    # Si no es AJAX, redirigir al carrito
    return redirect('store:cart')

# Checkout
def checkout(request):
    cart = get_cart_from_session(request)
    
    if not cart:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('store:product_list')
    
    cart_items = []
    total = 0
    
    for product_id, item_data in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item_data.get('quantity', 1)
        subtotal = product.price * quantity
        total += subtotal
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Crear orden
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                total_amount=total,
                pickup_time=timezone.now() + timedelta(hours=1),  # Tiempo de recogida por defecto (1 hora)
            )
            
            # Crear items de orden
            for product_id, item_data in cart.items():
                product = Product.objects.get(id=product_id)
                quantity = item_data.get('quantity', 1)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )
            
            # Limpiar carrito
            request.session['cart'] = {}
            
            # Redireccionar a la página de confirmación
            return redirect('store:order_confirmation', order_number=order.order_number)
    else:
        form = CheckoutForm()
        if request.user.is_authenticated:
            form.fields['customer_name'].initial = request.user.get_full_name() or request.user.username
            form.fields['customer_email'].initial = request.user.email
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_confirmation.html', context)

# Panel de administrador
def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('store:admin_dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and is_admin(user):
                login(request, user)
                return redirect('store:admin_dashboard')
            else:
                messages.error(request, "Credenciales inválidas o usuario no es administrador.")
    else:
        form = AdminLoginForm()
    
    return render(request, 'admin_panel/login.html', {'form': form})

# Actualización de la vista admin_dashboard

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Establecer hora de verificación para el seguimiento de nuevos pedidos
    request.session['last_orders_check'] = timezone.now().isoformat()
    
    # Resumen de pedidos
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    completed_orders = Order.objects.filter(status='completed').count()
    
    # Estadísticas rápidas
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today).count()
    
    # Solo contar ingresos de pedidos completados (ventas reales)
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'  # Solo pedidos completados
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Pedidos recientes - mostrar los más recientes primero
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    orders_queryset = Order.objects.all()
    
    # Filtrar por estado si se especifica
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders_queryset = orders_queryset.filter(status=status_filter)
    
    # Filtrar por búsqueda si se proporciona
    if search_query:
        orders_queryset = orders_queryset.filter(
            Q(customer_name__icontains=search_query) |
            Q(order_number__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Ordenar por fecha de creación (más recientes primero)
    orders = orders_queryset.order_by('-created_at')
    
    # Contar pedidos por estado para los filtros
    pending_count = Order.objects.filter(status='pending').count()
    processing_count = Order.objects.filter(status='processing').count()
    completed_count = Order.objects.filter(status='completed').count()
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'completed_count': completed_count,
    }
    return render(request, 'admin_panel/orders.html', context)

@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'admin_panel/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_update_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Pedido #{order.order_number} actualizado correctamente.")
            return redirect('store:admin_orders')
    else:
        form = OrderUpdateForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'admin_panel/update_order.html', context)

# Actualización de la vista admin_statistics

@login_required
@user_passes_test(is_admin)
def admin_statistics(request):
    # Estadísticas de ventas por día (últimos 7 días)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    daily_orders = []
    daily_revenue = []
    
    current_date = start_date
    while current_date <= end_date:
        # Contar todos los pedidos (para estadísticas de volumen)
        orders_count = Order.objects.filter(created_at__date=current_date).count()
        
        # Contar solo pedidos completados para ingresos (ventas reales)
        revenue = Order.objects.filter(
            created_at__date=current_date,
            status='completed'  # Solo pedidos completados
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        daily_orders.append({
            'date': current_date.strftime('%d/%m'),
            'count': orders_count,
        })
        
        daily_revenue.append({
            'date': current_date.strftime('%d/%m'),
            'amount': float(revenue),
        })
        
        current_date += timedelta(days=1)
    
    # Productos más vendidos (solo de pedidos completados)
    top_products = OrderItem.objects.filter(
        order__status='completed'  # Solo productos de pedidos completados
    ).values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Distribución de estados de pedidos
    status_distribution = list(Order.objects.values('status').annotate(count=Count('id')))
    
    # Totales generales para KPIs
    total_orders = Order.objects.count()
    
    # Total ventas (solo pedidos completados)
    total_revenue = Order.objects.filter(
        status='completed'  # Solo pedidos completados
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Ticket promedio (solo pedidos completados)
    completed_orders_count = Order.objects.filter(status='completed').count()
    average_ticket = total_revenue / completed_orders_count if completed_orders_count > 0 else 0
    
    # Productos vendidos (solo pedidos completados)
    total_products_sold = OrderItem.objects.filter(
        order__status='completed'  # Solo productos de pedidos completados
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Serializar los datos para JSON
    daily_orders_json = json.dumps(daily_orders)
    daily_revenue_json = json.dumps(daily_revenue)
    status_distribution_json = json.dumps(status_distribution)
    
    context = {
        'daily_orders': daily_orders_json,
        'daily_revenue': daily_revenue_json,
        'top_products': top_products,
        'status_distribution': status_distribution_json,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_ticket': average_ticket,
        'total_products_sold': total_products_sold,
        'completed_orders_count': completed_orders_count,
    }
    return render(request, 'admin_panel/statistics.html', context)

# Actualización de la vista api_order_counts

@login_required
@user_passes_test(is_admin)
def api_order_counts(request):
    """
    API para obtener contadores de pedidos para actualización en tiempo real.
    """
    try:
        # Obtener la última vez que se cargó la página
        last_check = request.session.get('last_orders_check')
        now = timezone.now()
        
        # Contar pedidos nuevos desde la última verificación
        new_orders = 0
        if last_check:
            try:
                last_check_time = timezone.datetime.fromisoformat(last_check)
                new_orders = Order.objects.filter(
                    created_at__gt=last_check_time,
                    status='pending'
                ).count()
            except (ValueError, TypeError) as e:
                print(f"Error al convertir fecha: {e}")
                # Si hay un error al convertir la fecha, reiniciar
                new_orders = 0
        
        # Obtener conteos actuales
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        completed_orders = Order.objects.filter(status='completed').count()
        
        # Estadísticas de hoy - SOLO contar pedidos COMPLETADOS para ingresos
        today = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today).count()
        today_completed_orders = Order.objects.filter(
            created_at__date=today, 
            status='completed'
        ).count()
        
        # Los ingresos solo se calculan basados en pedidos completados
        today_revenue = Order.objects.filter(
            created_at__date=today,
            status='completed'  # Solo contar ventas reales (pedidos completados)
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Almacenar la hora actual para la próxima verificación
        request.session['last_orders_check'] = now.isoformat()
        
        # Devolver los datos como JSON
        return JsonResponse({
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'completed_orders': completed_orders,
            'today_orders': today_orders,
            'today_completed_orders': today_completed_orders,
            'today_revenue': float(today_revenue),
            'new_orders': new_orders,
            'last_check': last_check,
            'current_check': now.isoformat(),
        })
    except Exception as e:
        print(f"Error en api_order_counts: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)
        
# Vista para la página de prueba
@login_required
@user_passes_test(is_admin)
def admin_test(request):
    """
    Página de prueba para el sistema de notificaciones.
    """
    return render(request, 'admin_panel/test.html')

# store/views.py (añadir esta vista)

def cart_test(request):
    """
    Página de prueba para diagnosticar problemas con el carrito.
    """
    # Obtener todos los productos disponibles
    products = Product.objects.filter(available=True)[:6]
    
    context = {
        'products': products,
    }
    return render(request, 'store/cart_test.html', context)