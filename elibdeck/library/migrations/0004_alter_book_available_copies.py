# Generated by Django 5.1.3 on 2024-12-30 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_book_issue_period_book_late_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='available_copies',
            field=models.PositiveIntegerField(default=0),
        ),
    ]