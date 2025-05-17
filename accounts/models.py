# accounts/models.py

from django.db import models
from django.contrib.auth.models import User

# Si necesitamos extender el modelo User en el futuro
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        
    def __str__(self):
        return f"Perfil de {self.user.username}"