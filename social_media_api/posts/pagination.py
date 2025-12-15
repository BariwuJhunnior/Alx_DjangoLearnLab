from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
  # Sets the default number of items per page (e.g., 10 posts/comments)
  page_size = 10

  #Allows the client to request a different page size using a query parameter (e.g., ?page_size=20)
  page_size_query_param = 'page_size'

  #Defines the maximum page size a client can request
  max_page_size = 100