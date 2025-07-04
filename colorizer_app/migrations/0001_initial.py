# Generated by Django 4.2.7 on 2025-05-27 08:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ColorizedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_image', models.ImageField(upload_to='uploads/')),
                ('colorized_image', models.ImageField(blank=True, null=True, upload_to='colorized/')),
                ('color_hex', models.CharField(blank=True, max_length=10)),
                ('intensity', models.FloatField(default=0.7)),
                ('edge_smooth', models.IntegerField(default=2)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
