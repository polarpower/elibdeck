# Generated by Django 5.1.3 on 2025-01-13 15:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_borrowrecord_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookrating',
            name='rating',
            field=models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='feedback_images/')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.studentprofile')),
            ],
        ),
        migrations.DeleteModel(
            name='Complaint',
        ),
    ]
