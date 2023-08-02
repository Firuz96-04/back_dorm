# Generated by Django 4.2.2 on 2023-07-14 04:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dormitory', '0035_delete_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('pay_date', models.DateField()),
                ('test_book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dormitory.testbooking')),
            ],
        ),
    ]
