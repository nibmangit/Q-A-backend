import django_filters
from .models import Question

class QuestionFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    author = django_filters.CharFilter(field_name="author__email", lookup_expr='iexact')
    tag = django_filters.CharFilter(method="filter_by_tag")
    tags = django_filters.BaseInFilter(field_name="tags__id", lookup_expr="in")

    class Meta:
        model = Question
        fields = ["category","tag", "tags", "author"] 

    def filter_by_tag(self, queryset, name, value): 
        return queryset.filter(tags__name__iexact=value)