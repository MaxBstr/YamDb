from django.contrib import admin

from .models import Category, Genre, Review, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
        'bio',
        'confirmation_code',
        'role'
    )


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category'
    )
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-empty-'


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'title', 'score')


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
