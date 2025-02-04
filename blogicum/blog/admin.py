from django.contrib import admin

from .models import Post, Category, Location, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'is_published',
        'category',
        'location'
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('is_published', 'category')
    list_display_links = ('title',)


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
