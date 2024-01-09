import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST

from .models import Book, Page
from .queue_helper import create_page_task, create_image_task

logger = logging.getLogger(__name__)

# TODO: remove from here, leave in login flow
@ensure_csrf_cookie
def list_books(request):
    limit = request.GET.get('limit', 10)
    offset = request.GET.get('offset', 0)

    books = Book.objects.all()
    return JsonResponse({
        "books": [{
            "id": b.id,
            "title": b.title,
        } for b in books[offset:(limit+offset)]]
    })

def get_book(request):
    book_id = request.GET.get('book_id')

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
        "owner": book.owner.username if book.owner else None,
        "views": book.views,
    })

# TODO: FIX CSRF WHEN HTTPS IS ENABLED
@csrf_exempt
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
    # system_prompt = json.dumps({
    #     'text': (
    #         "The response will be a paragraph of a short novel that continues the user input. "
    #         f"The novel is titled '{title}'. "
    #         "The paragraph itself must be the only content of the response, no introduction or greetings are allowed in the response, just the paragraph itself."
    #     ),
    #     'illustration': (
    #         "The footer text of an illustration sitting next to the paragraph given by the user. "
    #         "The footer text itself must be the only content of the response, no introduction or greetings are allowed in the response, just the footer text itself."
    #     )
    # })

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

    return JsonResponse({
        'book_id': book.id,
        'page_id': first_page.id
    }, status=201)


def get_page(request):
    book_id = request.GET.get('book_id')
    page_number = request.GET.get('page_number')
    page_id = request.GET.get('page_id')
    page = None

    if page_id:
        page = Page.objects.get(id=page_id)
    else:
        book = Book.objects.get(id=book_id)
        if not book:
            return JsonResponse({'error': 'Book not found'}, status=404)
        page = Page.objects.get(book=book, number=page_number)

    if not page:
        return JsonResponse({'error': 'Page not found'}, status=404)

    return JsonResponse({
        'id': page.id,
        'number': page.number,
        'text': page.content.get('text'),
        'img': page.image_url or None,
        'footer': page.content.get('illustration'),
        'input': page.user_input or None
    })

# TODO: FIX CSRF WHEN HTTPS IS ENABLED
@csrf_exempt
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

# TODO: FIX CSRF WHEN HTTPS IS ENABLED
@csrf_exempt
@require_POST
def resend_task(request):
    # TODO: check better when this endpoint can be called
    book_id = request.POST.get('book_id')
    page_id = request.POST.get('page_id')
    task_type = request.POST.get('task_type', 'page')

    print(book_id)
    print(page_id)
    print(task_type)

    if not book_id and not page_id:
        return JsonResponse({'error': 'Wrong request'}, status=400)

    if task_type == 'page':
        book = Book.objects.get(id=book_id)
        pages = list(Page.objects.filter(book=book).order_by('number'))
        create_page_task(book, pages)
        return JsonResponse({'page_id': pages[-1].id}, status=201)
    elif task_type == 'image':
        page = Page.objects.get(id=page_id)
        create_image_task(page)
        return JsonResponse({'page_id': page.id}, status=201)

@require_POST
@csrf_exempt
def write_page(request):
    # TODO: sign request and check signature, since it's an internal call
    logger.info("write_page called")
    page_id = request.POST['page_id']
    content = request.POST.get('content')
    image_url = request.POST.get('image_url')

    logger.info(f"page_id: {page_id}")
    logger.info(f"content: {content}")
    logger.info(f"image_url: {image_url}")

    page = Page.objects.get(id=page_id)

    if content:
        try:
            page.content = json.loads(content)
        except json.decoder.JSONDecodeError:
            page.content = json.loads(content + '}')
        page.save()
        create_image_task(page)
    elif image_url:
        page.image_url = image_url
        page.save()

    return JsonResponse({'message': 'success'})
