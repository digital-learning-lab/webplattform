from haystack.backends import SQ
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.filters import BaseFilterBackend


class SolrTagFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        q = request.GET.get('q', '')
        if len(q) >= 3:
            q = AutoQuery(request.GET.get('q', ''))
            sqs = SearchQuerySet().filter(SQ(tags=q) | SQ(name=q) | SQ(teaser=q) | SQ(subjects=q) |
                                          SQ(operating_systems=q))
            sqs.query.boost_fields = {'tags': 2, 'name': 3}
            pks = list(set(sqs.values_list('pk', flat=True)))
            return queryset.filter(pk__in=pks)
        else:
            return queryset


class SortingFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        sorting = request.GET.get('sorting', 'az')
        if sorting == 'az':
            return queryset.order_by('name')
        elif sorting == 'latest':
            return queryset.order_by('created')
        elif sorting == '-latest':
            return queryset.order_by('-created')
        else:
            return queryset.order_by('-name')
