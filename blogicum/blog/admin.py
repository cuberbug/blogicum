from django.contrib import admin

from .models import Category, Location, Post


class PostInLine(admin.TabularInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInLine,)
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = ('is_published',)
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInLine,)
    list_display = (
        'name',
        'is_published',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'text',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
        'pub_date',
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
