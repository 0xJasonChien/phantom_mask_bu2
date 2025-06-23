from typing import Self

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models.query import QuerySet
from django.http import HttpRequest
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView


class FullTextSearchFilter(SearchFilter):
    """
    implement full text search by using SearchVector and SearchQuery
    p.s. reference from https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/search/#the-search-lookup
    """

    def filter_queryset(
        self: Self,
        request: HttpRequest,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:

        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        search_query = SearchQuery('')
        for term in search_terms:
            search_query |= SearchQuery(term)

        search_vector = SearchVector(*search_fields)

        # descending to show the most relevant to the search_terms
        return queryset.annotate(
            rank=SearchRank(search_vector, search_query),
        ).order_by('-rank')
