import asyncio
import logging
import os
import sys

from aiohttp import ClientSession, ClientConnectorError
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_site.settings")
import django

django.setup()

from quotes.models import Author, Quote, Tag  # noqa

logging.basicConfig(level=logging.INFO)


async def fetch_page(session: ClientSession, url: str) -> str:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.error(f"Failed to fetch {url}: Status {response.status}")
                return ""
    except ClientConnectorError as err:
        logging.error(f"Connection error: {err}")
        return ""


async def parse_quotes(page: str) -> list:
    soup = BeautifulSoup(page, 'lxml')
    quotes = []
    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").text.strip()
        author = quote.find("small", class_="author").text.strip()
        tags = [tag.text.strip() for tag in quote.find_all("a", class_="tag")]
        quotes.append({"quote": text, "author": author, "tags": tags})
        logging.info(f"parsed quote by {author}")
    return quotes


async def parse_author(session: ClientSession, author_url: str) -> dict:
    page = await fetch_page(session, author_url)
    if page:
        soup = BeautifulSoup(page, 'lxml')
        author_details = soup.find("div", class_="author-details")

        author_biography = {
            "name": author_details.find("h3", class_="author-title").text.strip(),
            "born_date": author_details.find("span", class_="author-born-date").text.strip(),
            "born_location": author_details.find("span", class_="author-born-location").text.strip(),
            "description": author_details.find("div", class_="author-description").text.strip()
        }
        logging.info(f'fetched biography of {author_biography["name"]}')
        return author_biography


async def scrape_quotes_and_authors():
    base_url = "https://quotes.toscrape.com"
    authors_urls = set()
    quotes = []
    authors = []

    async with ClientSession() as session:
        page_tasks = [fetch_page(session, f"{base_url}/page/{i}/") for i in range(1, 11)]
        pages = await asyncio.gather(*page_tasks)

        for page in pages:
            if page:
                quotes.extend(await parse_quotes(page))
                soup = BeautifulSoup(page, 'lxml')
                for quote in soup.find_all("div", class_="quote"):
                    authors_urls.add(base_url + quote.find("a")["href"])

        author_tasks = [parse_author(session, url) for url in authors_urls]
        authors_data = await asyncio.gather(*author_tasks)
        authors = [author for author in authors_data if author]

    await save_to_db(authors, quotes)
    logging.info("All data successfully scraped and saved to DB.")


@sync_to_async
def save_to_db(authors: list[dict], quotes: list[dict]):
    existing_authors = set(Author.objects.values_list("name", flat=True))
    new_authors = [Author(**author) for author in authors if author["name"] not in existing_authors]
    Author.objects.bulk_create(new_authors, ignore_conflicts=True)

    authors_map = {a.name: a for a in Author.objects.all()}

    all_tags = {t.name: t for t in Tag.objects.all()}
    new_tag_names = {tag for q in quotes for tag in q["tags"]} - all_tags.keys()
    new_tags = [Tag(name=name) for name in new_tag_names]
    Tag.objects.bulk_create(new_tags, ignore_conflicts=True)
    all_tags.update({t.name: t for t in Tag.objects.filter(name__in=new_tag_names)})

    existing_quotes = set(Quote.objects.values_list("quote", flat=True))
    new_quotes = []
    quote_tags_map = {}
    for quote_data in quotes:
        if quote_data["quote"] in existing_quotes:
            continue
        author = authors_map.get(quote_data["author"])
        if not author:
            continue
        quote_obj = Quote(quote=quote_data["quote"], author=author)
        new_quotes.append(quote_obj)
        quote_tags_map[quote_data["quote"]] = [all_tags[tag] for tag in quote_data["tags"] if tag in all_tags]

    Quote.objects.bulk_create(new_quotes)

    for quote in Quote.objects.filter(quote__in=quote_tags_map.keys()):
        quote.tags.set(quote_tags_map[quote.quote])

    return {
        'authors_count': len(new_authors),
        'quotes_count': len(new_quotes),
        'tags_count': len(new_tags)
    }


def main():
    asyncio.run(scrape_quotes_and_authors())
