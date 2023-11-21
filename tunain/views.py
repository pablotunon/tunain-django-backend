from django.http import JsonResponse


def hello(request):
    return JsonResponse({'data': 'hello world'})


def next_page(request):
    return JsonResponse({
        'text': 'asasdasd',
        'img': 'basasdasd',
        'footer': 'casdasdasda',
        'input': 'deasdas'
    })
