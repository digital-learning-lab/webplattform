from haystack.backends import SQ
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.filters import BaseFilterBackend


class SolrTagFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', '')
        if len(q) >= 3:
            q = AutoQuery(request.GET.get('q', ''))
            sqs = SearchQuerySet().filter(SQ(tags=q))
            sqs.query.boost_fields = {'tags': 2}
            pks = list(set(sqs.values_list('pk', flat=True)))
            return queryset.filter(pk__in=pks)
        else:
            return queryset
