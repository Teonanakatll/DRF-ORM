from rest_framework.pagination import PageNumberPagination


class BookGPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10
    # ordering = ['-view_created_at']

# class BookGLinkPagination(PageNumberPagination):
#     page_size = 2
#     page_size_query_param = 'page_size'
#     max_page_size = 3
