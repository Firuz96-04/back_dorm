# Generated by Django 4.2.2 on 2023-08-21 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dormitory', '0049_student_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.CharField(choices=[('0', 'женшина'), ('1', 'мужчина')], max_length=1),
        ),
    ]