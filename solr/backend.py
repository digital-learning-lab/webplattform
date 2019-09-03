from haystack.backends import BaseEngine
from haystack.backends.solr_backend import SolrSearchBackend, SolrSearchQuery


class CustomSolrSearchBackend(SolrSearchBackend):
    def get_backend(self):
        pass

    def build_schema(self, fields):
        content_field_name = ''
        schema_fields = []

        for field_name, field_class in fields.items():
            field_data = {
                'field_name': field_class.index_fieldname,
                'type': 'text_german',
                'indexed': 'true',
                'stored': 'true',
                'multi_valued': 'false',
            }

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            # DRL_FIXME: Perhaps move to something where, if none of these
            #            checks succeed, call a custom method on the form that
            #            returns, per-backend, the right type of storage?
            if field_class.field_type in ['date', 'datetime']:
                field_data['type'] = 'pdate'
            elif field_class.field_type == 'integer':
                field_data['type'] = 'plong'
            elif field_class.field_type == 'float':
                field_data['type'] = 'pfloat'
            elif field_class.field_type == 'boolean':
                field_data['type'] = 'boolean'
            elif field_class.field_type == 'ngram':
                field_data['type'] = 'ngram'
            elif field_class.field_type == 'edge_ngram':
                field_data['type'] = 'edge_ngram'
            elif field_class.field_type == 'location':
                field_data['type'] = 'location'

            if field_class.is_multivalued:
                field_data['multi_valued'] = 'true'

            if field_class.stored is False:
                field_data['stored'] = 'false'

            # Do this last to override `text` fields.
            if field_class.indexed is False:
                field_data['indexed'] = 'false'

                # If it's text and not being indexed, we probably don't want
                # to do the normal lowercase/tokenize/stemming/etc. dance.
                if field_data['type'] == 'text_en':
                    field_data['type'] = 'string'

            # If it's a ``FacetField``, make sure we don't postprocess it.
            if hasattr(field_class, 'facet_for'):
                # If it's text, it ought to be a string.
                if field_data['type'] == 'text_en':
                    field_data['type'] = 'string'

            schema_fields.append(field_data)

        return (content_field_name, schema_fields)


class CustomSolrSearchQuery(SolrSearchQuery):

    def build_params(self, spelling_query=None, **kwargs):
        from haystack import connections
        search_kwargs = super(CustomSolrSearchQuery, self).build_params(spelling_query, **kwargs)

        search_kwargs['defType'] = 'dismax'
        search_kwargs['mm'] = 3

        # WARNING: major hack
        try:
            boost_fields = (i[0] for i in self.query_filter.children[0].children)
        except Exception:
            boost_fields = list()
        l = []
        for field in boost_fields:
            boost = connections[self._using].get_unified_index().fields[field].boost
            l.append(f'{field}^{boost}')
        search_kwargs['qf'] = ' '.join(l)
        return search_kwargs


class CustomSolrEngine(BaseEngine):
    backend = CustomSolrSearchBackend
    query = CustomSolrSearchQuery
