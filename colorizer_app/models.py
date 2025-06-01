from django.db import models
from django.utils import timezone

class ColorizedImage(models.Model):
    """Model to store uploaded and colorized images"""
    original_image = models.ImageField(upload_to='uploads/')
    colorized_image = models.ImageField(upload_to='colorized/', blank=True, null=True)
    color_hex = models.CharField(max_length=10, blank=True)
    intensity = models.FloatField(default=0.7)
    edge_smooth = models.IntegerField(default=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"ColorizedImage {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"