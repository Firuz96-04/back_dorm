# Generated by Django 4.2.2 on 2023-07-13 11:27

from django.db import migrations, models
import django.db.models.deletion
import dormitory.models


class Migration(migrations.Migration):

    dependencies = [
        ('dormitory', '0028_booking_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_start', models.DateField(default=dormitory.models.curr_date)),
                ('book_end', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('privilege', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dormitory.privilege')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dormitory.room')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dormitory.student')),
            ],
            options={
                'db_table': 'test_book',
            },
        ),
    ]
