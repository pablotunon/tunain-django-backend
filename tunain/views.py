import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST

from .models import Book, Page
from .queue_helper import create_page_task

logger = logging.getLogger(__name__)


def list_books(request):
    limit = request.GET.get('limit', 10)
    offset = request.GET.get('offset', 0)

    books = Book.objects.all()
    return [{
        "id": b.id,
        "title": b.title,
    } for b in books[offset:(limit+offset)]]

def get_book(request):
    book_id = request.GET.get('id', 1)

    if not book_id:
        return JsonResponse({'error': 'Wrong request'}, status=400)
    book = None
    try:
        book = Book.objects.get(id=book_id)
    except:
        return JsonResponse({'error': 'Book not found'}, status=404)

    return JsonResponse({
        "title": book.title,
        "initial_input": book.initial_input,
        "genre": book.genre,
        "art_extra_prompt": book.art_extra_prompt,
        "finished": book.finished,
        "owner": book.owner,
        "views": book.views,
    })

@require_POST
def create_book(request):
    title = request.POST.get('title')
    initial_input = request.POST.get('initial_input')

    if not title or not initial_input:
        return JsonResponse({'error': 'Wrong request'}, status=400)

    # All check passed, create a new book
    # TODO: escape title
    system_prompt = (
        "The response will be a paragraph of a short novel that continues the user input. "
        f"The novel is titled '{title}'. "
        "Response must be given in json format, with the following structure:"
"""
{
    "illustration": the footer text of an illustration sitting next to the paragraph that will be generated.
    "ended": a boolean representing whether the narrative reached the end or not.
    "text": the actual paragraph, novel style continuation of user input.
}
""")

    book = Book(
        system_prompt=system_prompt,
        title=title,
        initial_input=initial_input
        # TODO: owner
    )
    book.save()

    first_page = Page(
        book_id=book.id,
        number=1,
        content={},
        owner=book.owner
    )
    first_page.save()

    create_page_task(book, [first_page])

    return JsonResponse({'book_id': book.id, 'page_id': first_page.id}, status=201)


# TODO: remove from here, leave in login flow
@ensure_csrf_cookie
def get_page(request):
    book_id = request.GET.get('book_id', 1)
    page_number = request.GET.get('page_number', 1)

    book = Book.objects.get(id=book_id)
    if not book:
        return JsonResponse({'error': 'Book not found'}, status=404)

    page = Page.objects.get(book=book, number=page_number)

    return JsonResponse({
        'id': page.id,
        'number': page.number,
        'text': page.content.get('text'),
        'img': page.image_url or None,
        'footer': page.content.get('illustration'),
        'input': page.user_input or None
    })

@require_POST
def create_page(request):
    book_id = request.POST.get('book_id')
    input_str = request.POST.get('input')

    if not book_id or not input_str:
        return JsonResponse({'error': 'Wrong request'}, status=400)

    book = None
    try:
        book = Book.objects.get(id=book_id)
    except:
        return JsonResponse({'error': 'Book not found'}, status=404)

    if book.finished:
        return JsonResponse({'error': 'Book already finished'}, status=400)

    pages = list(Page.objects.filter(book=book).order_by('number'))
    last_page = pages[-1]

    if not last_page.content:
        return JsonResponse({'error': 'Last page still under generation'}, status=400)

    # All check passed, create a new page
    new_page = Page(
        book_id=book.id,
        number=last_page.number + 1,
        content={},
        owner=book.owner
    )
    new_page.save()

    last_page.user_input = input_str
    last_page.next_page = new_page
    last_page.save()

    create_page_task(book, pages + [new_page])

    return JsonResponse({'page_id': new_page.id}, status=201)


@require_POST
@csrf_exempt
def write_page(request):
    # TODO: sign request and check signature, since it's an internal call
    logger.info("write_page called")
    page_id = request.POST['page_id']
    content = request.POST['content']

    logger.info(f"page_id: {page_id}")
    logger.info(f"content: {content}")

    page = Page.objects.get(id=page_id)
    page.content = json.loads(content)
    page.save()

    return JsonResponse({'message': 'success'})
