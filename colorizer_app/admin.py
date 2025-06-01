from django.contrib import admin
from .models import ColorizedImage

@admin.register(ColorizedImage)
class ColorizedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'color_hex', 'intensity')
    list_filter = ('created_at',)
    search_fields = ('color_hex',)