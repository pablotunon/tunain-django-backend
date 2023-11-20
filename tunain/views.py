from django.http import JsonResponse


def hello(request):
    return JsonResponse({'data': 'hello world'})

