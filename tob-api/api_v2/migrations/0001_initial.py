# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-13 20:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('addressee', models.TextField(null=True)),
                ('civic_address', models.TextField(null=True)),
                ('city', models.TextField(null=True)),
                ('province', models.TextField(null=True)),
                ('postal_code', models.TextField(null=True)),
                ('country', models.TextField(null=True)),
                ('type', models.TextField(null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'address',
            },
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'claim',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('text', models.TextField(null=True)),
                ('type', models.TextField(null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'contact',
            },
        ),
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'credential',
            },
        ),
        migrations.CreateModel(
            name='CredentialType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('processor_config', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'credential_type',
            },
        ),
        migrations.CreateModel(
            name='Issuer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('did', models.TextField(unique=True)),
                ('name', models.TextField()),
                ('abbreviation', models.TextField()),
                ('email', models.TextField()),
                ('url', models.TextField()),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'issuer',
            },
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('text', models.TextField(null=True)),
                ('type', models.TextField(null=True)),
                ('language', models.TextField(null=True)),
                ('source_id', models.TextField(null=True)),
                ('is_legal', models.BooleanField(null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('credential', models.ManyToManyField(related_name='names', to='api_v2.Credential')),
            ],
            options={
                'db_table': 'name',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('full_name', models.TextField(null=True)),
                ('type', models.TextField(null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('credential', models.ManyToManyField(related_name='people', to='api_v2.Credential')),
            ],
            options={
                'db_table': 'person',
            },
        ),
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.TextField()),
                ('version', models.TextField()),
                ('origin_did', models.TextField()),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'schema',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('source_id', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'subject',
            },
        ),
        migrations.AlterUniqueTogether(
            name='schema',
            unique_together=set([('name', 'version', 'origin_did')]),
        ),
        migrations.AddField(
            model_name='credentialtype',
            name='issuer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credential_types', to='api_v2.Issuer'),
        ),
        migrations.AddField(
            model_name='credentialtype',
            name='schema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credential_types', to='api_v2.Schema'),
        ),
        migrations.AddField(
            model_name='credential',
            name='credential_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credentials', to='api_v2.CredentialType'),
        ),
        migrations.AddField(
            model_name='credential',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credentials', to='api_v2.Subject'),
        ),
        migrations.AddField(
            model_name='contact',
            name='credential',
            field=models.ManyToManyField(related_name='contacts', to='api_v2.Credential'),
        ),
        migrations.AddField(
            model_name='claim',
            name='credential',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='api_v2.Credential'),
        ),
        migrations.AddField(
            model_name='address',
            name='credential',
            field=models.ManyToManyField(related_name='addresses', to='api_v2.Credential'),
        ),
        migrations.AlterUniqueTogether(
            name='credentialtype',
            unique_together=set([('schema', 'issuer')]),
        ),
    ]
