from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.quotes_views, name="root"),
    path("author/<str:name>/", views.author_detail_views, name="author_detail"),
    path("tag/<str:name>/", views.search_by_tag, name="tag_quotes"),
    path("add_quote/", views.add_quote, name="add_quote"),
    path("add_author/", views.add_author, name="add_author"),
    path("pending/", views.pending_quotes, name="pending_quotes"),
    path('ajax/get_authors/', views.get_authors, name='get_authors'),
]
