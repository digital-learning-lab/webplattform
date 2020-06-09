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


class PolymorphicAttributeFilter(BaseFilterBackend):
    query_parameter_name = None
    field_name = None
    model = None

    def filter_queryset(self, request, queryset, view):
        if self.query_parameter_name.endswith('[]'):
            value = request.GET.getlist(self.query_parameter_name, None)
        else:
            value = request.GET.get(self.query_parameter_name, None)
        if value:
            query = {f'{self.model}___{self.field_name}': value}
            queryset = queryset.filter(**query)
        return queryset.distinct()


class ToolStatusFilter(PolymorphicAttributeFilter):
    model = 'Tool'
    query_parameter_name = 'status'
    field_name = 'status'


class ToolApplicationFilter(PolymorphicAttributeFilter):
    model = 'Tool'
    query_parameter_name = 'applications[]'
    field_name = 'applications__name__in'


class ToolOperationSystemFilter(PolymorphicAttributeFilter):
    model = 'Tool'
    query_parameter_name = 'operatingSystems[]'
    field_name = 'operating_systems__pk__in'


class ToolDataPrivacyFilter(PolymorphicAttributeFilter):
    model = 'Tool'
    query_parameter_name = 'dataPrivacy'
    field_name = 'privacy'
