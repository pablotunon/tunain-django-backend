from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import Book, Page
from .queue_helper import create_page_task

# TODO: remove from here, leave in login flow
@ensure_csrf_cookie
def next_page(request):
    print(request.GET)
    book_id = request.GET.get('book_id', 1)
    page_number = request.GET.get('page_number', 1)

    book = Book.objects.get(id=book_id)
    if not book:
        return JsonResponse({'error': 'Book not found'}, status=404)

    page = Page.objects.get(book=book, number=page_number)

    print(page.content)

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
    print(request.POST)
    book_id = request.POST.get('book_id')
    input_str = request.POST.get('input')

    if not book_id or not input_str:
        return JsonResponse({'error': 'Wrong parameters'}, status=400)

    book = None
    try:
        book = Book.objects.get(id=book_id)
    except:
        return JsonResponse({'error': 'Book not found'}, status=404)

    if book.finished:
        return JsonResponse({'error': 'Book already finished'}, status=400)

    pages = list(Page.objects.filter(book=book).order_by('number'))
    print('print page numbers')
    for p in pages:
        print(p.number)

    last_page = pages[-1]

    if not last_page.content:
        return JsonResponse({'error': 'Last page still under generation'}, status=400)

    # All check passed, create a new page
    new_page = Page(
        book_id=book.id,
        number=last_page.number + 1,
        content={}
    )
    new_page.save()

    last_page.user_input = input_str
    last_page.next_page = new_page
    last_page.save()

    create_page_task(book, pages + [new_page])

    return JsonResponse({'page_id': new_page.id}, status=201)
