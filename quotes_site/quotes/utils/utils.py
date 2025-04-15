from quotes.models import Tag


def get_top_tags():
    return Tag.objects.order_by("-visit_count")[:10]  # noqa
