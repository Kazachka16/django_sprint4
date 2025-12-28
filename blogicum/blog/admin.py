from django.contrib import admin
from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'pub_date', 
        'category',
        'location',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('is_published', 'category', 'pub_date')
    readonly_fields = ('created_at',)
    date_hierarchy = 'pub_date'
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'text', 'author', 'image')
        }),
        ('Даты и публикация', {
            'fields': ('pub_date', 'is_published', 'created_at')
        }),
        ('Классификация', {
            'fields': ('category', 'location')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'text', 'created_at', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('is_published', 'created_at')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
