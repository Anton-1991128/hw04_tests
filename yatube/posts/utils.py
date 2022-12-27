from django.core.paginator import Paginator
from django.conf import settings


def get_pagination(request, quaryset):
    paginator = Paginator(quaryset, settings.POSTS_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
