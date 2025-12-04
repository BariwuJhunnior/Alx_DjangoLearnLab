import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
  title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
  author = django_filters.CharFilter(field_name='author', lookup_expr='icontains')

  publication_year = django_filters.NumberFilter(field_name='publication_year')

  #Optional, filter by year range
  min_year = django_filters.NumberFilter(field_name='publication_year', lookup_expr='gte')
  max_year = django_filters.NumberFilter(field_name='publication_year', lookup_expr='lte')


  class Meta:
    model = Book
    fields = ['title', 'author', 'publication_year']