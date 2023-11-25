from django.http import JsonResponse
from .models import Book, Page


def next_page(request):
    print(request.GET)
    book_id = request.GET.get('book_id', 1)
    page_number = request.GET.get('page_number', 1)

    book = Book.objects.get(id=book_id)
    page = Page.objects.get(book=book, number=page_number)

    print(page.content)

    return JsonResponse({
        'text': page.content['text'],
        'img': page.image_url or None,
        'footer': page.content['illustration'],
        'input': page.user_input or None
    })

def create_page(request):
    if request.method == 'POST':
        print(request.POST)
    else:
        print(request.method)
