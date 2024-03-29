# Generated by Django 2.2.5 on 2019-10-19 22:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Object',
            fields=[
                ('name', models.TextField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('category', models.TextField(choices=[('Sports', 'Sports'), ('Kids', 'Kids'), ('News', 'News'), ('Politics', 'Politics'), ('Music', 'Music')])),
                ('video_file_path', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FrameObjectData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frame_no', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Object')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Video')),
            ],
        ),
    ]
