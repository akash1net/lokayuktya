# Register your models here.
from django.contrib import admin
from .models import *



admin.site.register(Gallery)
admin.site.register(Highlights)
admin.site.register(FAQ)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform_type', 'is_clickable', 'is_active', 'created_at')
    list_filter = ('platform_type', 'is_active', 'is_clickable')
    search_fields = ('title',)




@admin.register(Lokayukta)
class LokayuktaProfilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','image', 'lokayukta_status', 'user_position', 'is_active', 'created_at')
    list_filter = ('lokayukta_status', 'user_position', 'is_active')
    search_fields = ('title',)
    readonly_fields = ('created_at',)



@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('page_type', 'title', 'image','content')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'iso_code', 'phone_code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'iso_code', 'phone_code')
    ordering = ('name',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'country', 'is_active', 'created_at')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'code', 'country__name')
    ordering = ('country__name', 'name')