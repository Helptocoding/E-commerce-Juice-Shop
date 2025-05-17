# store/models.py

from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Precio")
    image = models.ImageField(upload_to='products/', verbose_name="Imagen", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoría")
    available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('processing', 'En proceso'),
        ('completed', 'Completado'),
    )
    
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Número de pedido")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    customer_name = models.CharField(max_length=100, verbose_name="Nombre del cliente")
    customer_email = models.EmailField(verbose_name="Email")
    customer_phone = models.CharField(max_length=15, verbose_name="Teléfono")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    pickup_time = models.DateTimeField(default=timezone.now, verbose_name="Hora de recogida")
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Pedido #{self.order_number}"
    
    def get_items_count(self):
        return self.items.count()
    
    def get_status_display_name(self):
        return dict(self.STATUS_CHOICES)[self.status]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Pedido")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    
    class Meta:
        verbose_name = "Item de pedido"
        verbose_name_plural = "Items de pedido"
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total(self):
        return self.price * self.quantity