# Generated by Django 5.2.2 on 2025-06-12 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_withdrawalrequest_card_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawalrequest',
            name='card_number',
            field=models.CharField(blank=True, default=None, max_length=30),
        ),
    ]
