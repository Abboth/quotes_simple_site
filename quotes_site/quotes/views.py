from .models import Quote, Author, Tag
from quotes.utils.utils import get_top_tags

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView


def quotes_views(request):
    quotes = Quote.objects.select_related("author").prefetch_related("tags").order_by("id")  # noqa

    paginator = Paginator(quotes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "quotes/index.html", context={"page_obj": page_obj, "top_tags": get_top_tags})


def author_detail_views(request, name):
    author = get_object_or_404(Author, name=name)
    return render(request, "quotes/author_detail.html", {"author": author})


def search_by_tag(request, name):
    tag = get_object_or_404(Tag, name=name)

    last_visit = request.session.get(f"last_visit_tag_{tag.id}")
    now = timezone.now().timestamp()
    if not last_visit or now - last_visit > 4:
        tag.visit_count += 1
        tag.save(update_fields=["visit_count"])
        request.session[f"last_visit_tag_{tag.id}"] = now

    quotes = tag.quote_set.select_related("author").prefetch_related("tags").order_by("id")
    paginator = Paginator(quotes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "quotes/tag_quotes.html",
                  context={"tag": tag, "page_obj": page_obj, "top_tags": get_top_tags})


def get_authors(request):
    query = request.GET.get('term', '')
    authors = Author.objects.filter(name__icontains=query).values_list('name', flat=True)  # noqa
    return JsonResponse(list(authors), safe=False)


def add_quote(request):
    return render(request, "quotes/add_quote.html")


def add_author(request):
    return render(request, "quotes/add_author.html")


def pending_quotes(request):
    return render(request, "quotes/pending.html")
