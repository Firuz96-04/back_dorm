from abc import ABC
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination, ABC):
    page_size = 5
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        page_size = request.query_params.get('page_size', self.page_size)
        if page_size is not None:
            return min(int(page_size), self.max_page_size)
        return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total': self.page.paginator.count,
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'current_page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })