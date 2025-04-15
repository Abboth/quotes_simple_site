from .models import CreateQuote, CreateAuthor


def pending_data_count(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return {}

    quotes_count = CreateQuote.objects.count()
    authors_count = CreateAuthor.objects.count()
    total = quotes_count + authors_count

    return {
        "pending_data_count": total,
        "pending_quotes_count": quotes_count,
        "pending_authors_count": authors_count,
    }
