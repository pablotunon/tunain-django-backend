"""
URL configuration for tunain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from . import core_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Core views
    path('login/cookie', core_views.login_set_cookie, name='login_cookie'),
    path('login', core_views.login_credentials, name='login'),
    path('logout', core_views.logout_view, name='logout'),
    path('permissions', core_views.permissions_view, name='permissions'),

    # Other views
    path('books/list', views.list_books, name='list-books'),
    path('book', views.get_book, name='book'),
    path('create-book', views.create_book, name='create-book'),
    path('page', views.get_page, name='page'),
    path('create-page', views.create_page, name='create-page'),
    path('write-page', views.write_page, name='write-page'),
    path('resend-task', views.resend_task, name='resend-task'),
]
