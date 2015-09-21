from django.contrib import admin
from core.models import (User, Profile, Service, Attribute, AttributeGroup, 
                         UserAttribute, UserLog, Event)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username','first_name','last_name','email','private','last_login','country')
    ordering = ('username',)
    list_filter = ('country','is_active','trial','delinquent')
    search_fields = ('username','first_name','last_name','email')


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name','label','priority','group')
    list_filter = ('priority',)
    ordering = ('priority','label')
    search_fields = ('name','label')


class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = ('name','label','priority')
    list_filter = ('priority',)
    ordering = ('priority','label')
    search_fields = ('name','label')
    

class UserAttributeAdmin(admin.ModelAdmin):
    list_display = ('__str__','attribute','user','service')
    list_filter = ('attribute','service')
    ordering = ('user',)
    search_fields = ('user__username','attribute__name')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__','user','service','created')
    list_filter = ('service',)
    ordering = ('user','service')
    search_fields = ('user__username','service__slug')


class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user','page','action','args','created')
    list_filter = ('page',)
    ordering = ('-created',)
    date_hierarchy = 'created'
    search_fields = ('user__username','page','action','args')



class EventAdmin(admin.ModelAdmin):
    list_display = ('created','user','attribute','value')
    list_filter = ('attribute',)
    ordering = ('-created',)
    date_hierarchy = 'created'


admin.site.register(Service)
admin.site.register(Event, EventAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeGroup, AttributeGroupAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserAttribute, UserAttributeAdmin)
admin.site.register(UserLog,UserLogAdmin)
