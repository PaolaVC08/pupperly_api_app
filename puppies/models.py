from django.db import models
from django.conf import settings

class Puppy(models.Model):
    name = models.CharField(max_length=100)  # Nombre del perrito
    breed = models.CharField(max_length=100)  # Raza del perrito
    #url = models.URLField()  # URL de la imagen
    description = models.TextField(blank=True)  # Descripción del perrito
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)#quien lo postea

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puppy = models.ForeignKey('puppies.Puppy', related_name='votes', on_delete=models.CASCADE)