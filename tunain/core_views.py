import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST


logger = logging.getLogger()


def health_check(request):
    return JsonResponse({'status': 'OK'})


@ensure_csrf_cookie
def login_set_cookie(request):
    return JsonResponse({"info": "CSRF cookie set"})


@require_POST
def login_credentials(request):
    """
    This function checks user credentials
    """
    username = request.POST.get("username")
    password = request.POST.get("password")
    if username is None or password is None:
        return JsonResponse(
            {"error": "Please enter username and password"},
            status=400,
        )
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"info": "Success"})
    return JsonResponse({"error": "Invalid credentials"}, status=400)


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"info": "Success"})


@ensure_csrf_cookie
@login_required
def permissions_view(request):
    """
    The frontend checks its cookie and gets the information to tweak the UI from this request
    Returns request user permissions
    """
    if request.user.has_perm('auth.view_permission'):
        return JsonResponse(request.user.to_dict(include_permissions=True))
    else:
        return JsonResponse(request.user.to_dict())
