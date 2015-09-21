# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import core.json_field
import django.contrib.auth.models
import django.utils.timezone
import decimal
import django.core.serializers.json
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True, verbose_name='username', max_length=30)),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('timezone', models.CharField(max_length=80, db_index=True, null=True)),
                ('avatar', models.ImageField(upload_to='', blank=True, null=True)),
                ('last_seen_activity', models.DateTimeField(blank=True, null=True)),
                ('bio', models.CharField(max_length=160, blank=True, null=True)),
                ('url', models.URLField(max_length=250, blank=True, null=True, verbose_name='Website')),
                ('private', models.BooleanField(help_text='Only logged-in users will be able to see your profile.', default=True)),
                ('imperial_units', models.BooleanField(default=False)),
                ('stripe_customer', models.CharField(max_length=250, blank=True, null=True)),
                ('country', models.CharField(max_length=150, blank=True, null=True)),
                ('weekly_email', models.BooleanField(default=True)),
                ('delinquent', models.BooleanField(default=False)),
                ('trial', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', verbose_name='groups', blank=True, related_name='user_set')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission', verbose_name='user permissions', blank=True, related_name='user_set')),
            ],
            options={
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=40)),
                ('priority', models.IntegerField(default=2)),
                ('value_type', models.SmallIntegerField(choices=[(0, 'Integer'), (1, 'Float'), (2, 'String'), (3, 'Period (min)'), (4, 'Time of day (min from midnight)'), (5, 'Percentage'), (6, 'Time of day (min from midday)')], default=0)),
                ('private_default', models.BooleanField(default=False)),
                ('correlation_offset', models.SmallIntegerField(default=0)),
                ('correlation_positive', models.CharField(max_length=160, blank=True, null=True)),
                ('correlation_negative', models.CharField(max_length=160, blank=True, null=True)),
                ('correlation_priority', models.IntegerField(help_text="Higher = everything else follows this, eg. the weather. You can't control the weather.", default=0)),
            ],
            options={
                'ordering': ['priority', 'label'],
            },
        ),
        migrations.CreateModel(
            name='AttributeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=40)),
                ('priority', models.IntegerField(default=2)),
            ],
            options={
                'ordering': ['priority', 'label'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('attribute_id', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('time', models.DateTimeField()),
                ('int_value', models.IntegerField(blank=True, null=True)),
                ('float_value', models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)),
                ('string_value', models.CharField(max_length=255, blank=True, null=True)),
                ('value_type', models.SmallIntegerField()),
                ('meta', core.json_field.JSONField(encode_kwargs={'cls': django.core.serializers.json.DjangoJSONEncoder}, default={}, null=True, decode_kwargs={'parse_float': decimal.Decimal})),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['service__type__order', 'service__name'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('slug', models.SlugField(max_length=60)),
                ('description', models.TextField(blank=True, null=True)),
                ('provides', models.TextField(blank=True, null=True)),
                ('requirements', models.TextField(blank=True, null=True)),
                ('settings', models.BooleanField(default=False)),
                ('external', models.BooleanField(default=False)),
                ('attributes', models.ManyToManyField(to='core.Attribute', blank=True, related_name='services')),
            ],
            options={
                'ordering': ['type__order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='UserAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True, verbose_name='Enabled')),
                ('private', models.BooleanField(default=False, verbose_name='Private')),
                ('attribute', models.ForeignKey(to='core.Attribute', related_name='users')),
                ('service', models.ForeignKey(to='core.Service', null=True, blank=True, related_name='user_attributes')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='attributes')),
            ],
            options={
                'ordering': ['service__type__order', 'attribute__group__priority', 'attribute__priority', 'attribute__name'],
            },
        ),
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('page', models.CharField(max_length=128, db_index=True)),
                ('action', models.CharField(max_length=128)),
                ('args', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='logs')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='service',
            field=models.ForeignKey(to='core.Service', related_name='users'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='profiles'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='group',
            field=models.ForeignKey(to='core.AttributeGroup', null=True, blank=True, related_name='attributes'),
        ),
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set([('user', 'service')]),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('email',)]),
        ),
    ]
