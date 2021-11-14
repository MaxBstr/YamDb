from django_filters import rest_framework as filters

from .models import Category, Genre, Title


class TitlesFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='contains'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='contains'
    )

    class Meta:
        model = Title
        fields = [
            'name',
            'genre',
            'category',
            'year'
        ]


class GenresFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Genre
        fields = ['name']


class CategoriesFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Category
        fields = ['name']
