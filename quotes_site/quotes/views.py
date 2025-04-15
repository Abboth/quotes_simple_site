from services.scraper import main as scraper  # NOQA
from .models import Quote, Author, Tag, CreateQuote, CreateAuthor
from quotes.utils.utils import get_top_tags  # noqa
from .forms import CreateQuoteForm, CreateAuthorForm

from celery import shared_task
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View


def is_moderator(user):
    return user.is_superuser


@shared_task
def scrape_quotes(request):
    try:
        if request.method == 'POST':
            scraper()
            messages.info(request, "Scraping started")
    except Exception as e:
        messages.error(request, f"Scraping failed: {str(e)}")

    return redirect('quotes:root')


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


@login_required
def add_quote(request):
    if request.method == "POST":
        form = CreateQuoteForm(request.POST)

        if form.is_valid():
            created_quote = form.save(commit=False)
            created_quote.created_by_user = request.user
            created_quote.save()

            tag_names = [tag.strip() for tag in form.cleaned_data["tags"].split(",") if tag.strip()]
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]  # noqa
            created_quote.tags.set(tags)

            messages.success(request, "Quote added and waiting for moderator approval.")
            return redirect("quotes:root")
    else:
        form = CreateQuoteForm()
    return render(request, "quotes/add_quote.html", {"form": form})


@login_required()
def add_author(request):
    if request.method == "POST":
        form = CreateAuthorForm(request.POST)
        if form.is_valid():
            created_author = form.save(commit=False)
            created_author.created_by_user = request.user
            created_author.save()
            messages.success(request, "Author added, and waiting for confirming by moderator")
            return redirect("quotes:root")
    else:
        form = CreateAuthorForm()
    return render(request, "quotes/add_author.html", context={"form": form})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_moderator), name='dispatch')
class PendingDataView(View):

    def get(self, request):
        authors = CreateAuthor.objects.all()  # noqa
        quotes = CreateQuote.objects.select_related("author").prefetch_related("tags")  # noqa
        return render(request, "quotes/pending_data.html",
                      context={"authors": authors,
                               "quotes": quotes
                               })

    def post(self, request):
        item_type = request.POST.get("type")
        action = request.POST.get("action")
        item_id = request.POST.get("id")

        if item_type == "author":
            return self.pending_authors(request, item_id, action)
        elif item_type == "quotes":
            return self.pending_quotes(request, item_id, action)

    @staticmethod
    def pending_quotes(request, item_id, action):
        try:
            pending_quote = CreateQuote.objects.get(id=item_id)  # noqa

            if action == "approve":
                quote = Quote.objects.create(  # noqa
                    quote=pending_quote.quote,
                    author=pending_quote.author,
                    created_by_user=pending_quote.created_by_user
                    if hasattr(pending_quote, "created_by_user") else None
                ).tags.set(pending_quote.tags.all())
                pending_quote.delete()
                messages.success(request, "Quote is approved and published.")
            elif action == "reject":
                pending_quote.delete()
                messages.warning(request, "Quote rejected and removed.")
        except CreateQuote.DoesNotExist as err:  # noqa
            messages.warning(request, f"Pending quote with ID {item_id} not found")

        return redirect("quotes:pending_data")

    @staticmethod
    def pending_authors(request, item_id, action):
        try:
            pending_author = CreateAuthor.objects.get(id=item_id)  # noqa

            if action == "approve":
                quote = Author.objects.create(  # noqa
                    name=pending_author.name,
                    born_date=pending_author.born_date,
                    born_location=pending_author.born_location,
                    description=pending_author.description,
                    created_by_user=pending_author.created_by_user if hasattr(pending_author,
                                                                              "created_by_user") else None
                )
                pending_author.delete()
                messages.success(request, "Quote is approved and published.")
            elif action == "reject":
                pending_author.delete()
                messages.warning(request, "Quote rejected and removed.")

        except CreateAuthor.DoesNotExist as err:  # noqa
            messages.warning(request, f"Pending author with ID {item_id} not found")

        return redirect("quotes:pending_data")
