from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_image, name='upload_image'),
    path('result/<int:image_id>/', views.result, name='result'),
    path('recolor/<int:image_id>/', views.recolor_image, name='recolor_image'),
]