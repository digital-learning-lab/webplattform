from haystack.backends import SQ
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.filters import BaseFilterBackend


class SolrTagFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', '')
        if q:
            q = AutoQuery(request.GET.get('q', ''))
            pks = queryset.values_list('pk', flat=True)
            sqs = SearchQuerySet().filter(SQ(tags=q))
            for i in sqs:
                print(i)
            return queryset
        else:
            return queryset
