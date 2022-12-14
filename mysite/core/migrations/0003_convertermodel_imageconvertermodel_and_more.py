# Generated by Django 4.1.3 on 2022-11-26 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_wordtopdfmodel_pdffile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConverterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('ConvertedFile', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageConverterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('convertedImage', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='WordtoPDFModel',
        ),
    ]
