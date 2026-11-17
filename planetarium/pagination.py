from rest_framework.pagination import PageNumberPagination


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ShowSessionPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
