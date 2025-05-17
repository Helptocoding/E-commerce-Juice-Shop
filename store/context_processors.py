# store/context_processors.py

def cart_processor(request):
    """
    Contexto para obtener la información del carrito desde cualquier template.
    """
    # Para depuración: imprimir el contenido del carrito
    cart = request.session.get('cart', {})
    print("Debug - Contenido del carrito:", cart)
    
    # Calcular cantidad
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    print("Debug - Cantidad total en carrito:", cart_count)
    
    # Calcular los items y el total del carrito
    cart_items = []
    cart_total = 0
    
    try:
        from .models import Product
        
        for product_id, item_data in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                quantity = item_data.get('quantity', 1)
                subtotal = product.price * quantity
                cart_total += subtotal
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal,
                })
                print(f"Debug - Producto en carrito: {product.name}, cantidad: {quantity}, subtotal: {subtotal}")
            except Product.DoesNotExist:
                # Si el producto ya no existe, lo quitamos del carrito
                print(f"Debug - Producto no encontrado: {product_id}")
                cart.pop(product_id, None)
                # Actualizamos el carrito en la sesión
                request.session['cart'] = cart
                request.session.modified = True
    except Exception as e:
        print(f"Error en cart_processor: {e}")
    
    return {
        'cart_count': cart_count,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }