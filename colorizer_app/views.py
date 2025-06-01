import os
import io
import base64
import os
import io
import base64
import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from .models import ColorizedImage
from .forms import ImageUploadForm
from .utils import (
    COLOR_PRESETS, 
    create_object_mask, 
    process_color_change,
    hex_to_rgb
)

def index(request):
    """Home page view with image upload form"""
    form = ImageUploadForm()
    color_presets = COLOR_PRESETS
    
    context = {
        'form': form,
        'color_presets': color_presets,
    }
    return render(request, 'colorizer_app/index.html', context)

def upload_image(request):
    """Handle image upload and initial processing"""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the form but don't commit yet
                colorized_image = form.save(commit=False)
                
                # Process the image
                original_pil = Image.open(colorized_image.original_image)
                
                # Get max image size from settings
                max_size = getattr(settings, 'MAX_IMAGE_SIZE', 512)
                
                # Resize image to reduce memory usage
                if max(original_pil.size) > max_size:
                    scale = max_size / max(original_pil.size)
                    new_width = int(original_pil.size[0] * scale)
                    new_height = int(original_pil.size[1] * scale)
                    original_pil = original_pil.resize((new_width, new_height), Image.LANCZOS)
                
                # Save the model first to get an ID
                colorized_image.save()
                
                # Create mask and save it for future use using rembg
                mask = create_object_mask(original_pil, method="rembg", max_size=max_size)
                mask_path = os.path.join(settings.MEDIA_ROOT, f'masks/mask_{colorized_image.id}.png')
                os.makedirs(os.path.dirname(mask_path), exist_ok=True)
                mask.save(mask_path)
                
                # Process with selected color
                color_hex = form.cleaned_data['color_hex']
                intensity = form.cleaned_data['intensity']
                edge_smooth = form.cleaned_data['edge_smooth']
                
                result_image, _ = process_color_change(
                    original_pil, 
                    color_hex, 
                    intensity, 
                    edge_smooth, 
                    mask
                )
                
                # Save the colorized image with compression
                buffer = io.BytesIO()
                if result_image.mode == 'RGBA':
                    result_image = result_image.convert('RGB')
                result_image.save(buffer, format='JPEG', quality=85, optimize=True)
                image_file = ContentFile(buffer.getvalue())
                
                # Use JPEG extension for faster loading
                file_name = os.path.splitext(os.path.basename(colorized_image.original_image.name))[0]
                colorized_image.colorized_image.save(
                    f"colorized_{file_name}.jpg", 
                    image_file
                )
                
                # Update the model
                colorized_image.color_hex = color_hex
                colorized_image.intensity = intensity
                colorized_image.edge_smooth = edge_smooth
                colorized_image.save()
                
                # Force garbage collection to free memory
                import gc
                gc.collect()
                
                return redirect('result', image_id=colorized_image.id)
                
            except Exception as e:
                print(f"Error in upload_image: {str(e)}")
                # Return to form with error message
                return render(request, 'colorizer_app/index.html', {
                    'form': form, 
                    'color_presets': COLOR_PRESETS,
                    'error_message': 'An error occurred while processing your image. Please try again with a different image.'
                })
    else:
        form = ImageUploadForm()
    
    return render(request, 'colorizer_app/index.html', {'form': form, 'color_presets': COLOR_PRESETS})

def result(request, image_id):
    """Display the colorized image result"""
    try:
        colorized_image = ColorizedImage.objects.get(id=image_id)
        context = {
            'colorized_image': colorized_image,
            'color_presets': COLOR_PRESETS,
        }
        return render(request, 'colorizer_app/result.html', context)
    except ColorizedImage.DoesNotExist:
        return redirect('index')

def recolor_image(request, image_id):
    """API endpoint to recolor an existing image with new parameters"""
    if request.method == 'POST':
        try:
            colorized_image = ColorizedImage.objects.get(id=image_id)
            
            # Get parameters from POST
            color_hex = request.POST.get('color_hex', '#FF3333')
            intensity = float(request.POST.get('intensity', 0.7))
            edge_smooth = int(request.POST.get('edge_smooth', 2))
            
            # Open original image
            original_pil = Image.open(colorized_image.original_image.path)
            
            # Resize image to reduce memory usage
            max_size = getattr(settings, 'MAX_IMAGE_SIZE', 512)
            if max(original_pil.size) > max_size:
                scale = max_size / max(original_pil.size)
                new_width = int(original_pil.size[0] * scale)
                new_height = int(original_pil.size[1] * scale)
                original_pil = original_pil.resize((new_width, new_height), Image.LANCZOS)
            
            # Use cached mask if available or create new one
            mask_path = os.path.join(settings.MEDIA_ROOT, f'masks/mask_{colorized_image.id}.png')
            os.makedirs(os.path.dirname(mask_path), exist_ok=True)
            
            if os.path.exists(mask_path):
                mask = Image.open(mask_path)
            else:
                # Create a new mask using rembg
                mask = create_object_mask(original_pil, method="rembg", max_size=max_size)
                # Save mask for future use
                mask.save(mask_path)
            
            # Process with new color
            result_image, _ = process_color_change(
                original_pil, 
                color_hex, 
                intensity, 
                edge_smooth, 
                mask
            )
            
            # Save the new colorized image with compression for faster response
            buffer = io.BytesIO()
            # Use JPEG for faster saving, with high quality
            if result_image.mode == 'RGBA':
                result_image = result_image.convert('RGB')
            result_image.save(buffer, format='JPEG', quality=85, optimize=True)
            image_file = ContentFile(buffer.getvalue())
            
            # Update the model
            colorized_image.color_hex = color_hex
            colorized_image.intensity = intensity
            colorized_image.edge_smooth = edge_smooth
            
            # Delete old image if it exists
            if colorized_image.colorized_image:
                colorized_image.colorized_image.delete(save=False)
            
            # Use JPEG extension for faster loading
            file_name = os.path.splitext(os.path.basename(colorized_image.original_image.name))[0]
            colorized_image.colorized_image.save(
                f"colorized_{file_name}.jpg", 
                image_file
            )
            colorized_image.save()
            
            # Force garbage collection to free memory
            import gc
            gc.collect()
            
            return JsonResponse({
                'success': True,
                'image_url': colorized_image.colorized_image.url
            })
            
        except ColorizedImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
        except Exception as e:
            print(f"Error in recolor_image: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})