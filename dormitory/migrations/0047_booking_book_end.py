# Generated by Django 4.2.2 on 2023-08-04 04:37

from django.db import migrations, models
import dormitory.models


class Migration(migrations.Migration):

    dependencies = [
        ('dormitory', '0046_alter_payment_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='book_end',
            field=models.DateField(default=dormitory.models.curr_date),
        ),
    ]