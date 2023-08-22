from abc import ABC
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

import os
from datetime import date
import uuid


def upload_path(prefix, instance, filename):
    ext = filename.split('.')[-1]
    today = date.today().strftime('%Y/%m/%d')
    filename = f'{uuid.uuid4().hex[:16]}.{ext}'
    return '{prefix}/{today}/{filename}'.format(
        prefix=prefix,
        today=today,
        filename=filename)


def upload_photo(instance, filename):
    return upload_path('student/diploma', instance, filename)


class CustomPagination(PageNumberPagination, ABC):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        page_size = request.query_params.get('page_size', self.page_size)
        if page_size is not None:
            return min(int(page_size), self.max_page_size)
        return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total': self.page.paginator.count,
                'page_size': int(self.request.GET.get('page_size', self.page_size)),
                'current_page_number': self.page.number,
                'total_pages': self.page.paginator.num_pages,
            },
            'results': data
        })

        # 'links': {
        #     'next': self.get_next_link(),
        #     'previous': self.get_previous_link()
        # },
        # 'total': self.page.paginator.count,
        # 'page_size': int(self.request.GET.get('page_size', self.page_size)),
        # 'current_page_number': self.page.number,
        # 'total_pages': self.page.paginator.num_pages,
        # 'results': data
