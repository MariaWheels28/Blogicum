from django.contrib import admin

from .models import Post, Category, Location, Comment


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


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
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_at')
    list_filter = ('post', 'author')
    search_fields = ('text', 'author__username')


admin.site.register(Category)
admin.site.register(Location)
