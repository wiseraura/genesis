from app.models import Tag, Category
from django.template import Library

register = Library()

@register.inclusion_tag('components/main_categories.html', takes_context=True)
def category_list(context):
    categories = Category.objects.all()
    return {
        'request': context['request'],
        'categories': categories
    }

@register.inclusion_tag('components/main_tags.html', takes_context=True)
def tag_list(context):
    tags = Tag.objects.all()
    return {
        'request': context['request'],
        'tags': tags
    }

@register.inclusion_tag('components/article_categories.html', takes_context=True)
def article_category_list(context):
    page = context['page']
    article_categories = page.categories.all()
    return {
        "request": context['request'],
        "article_categories": article_categories
    }

@register.inclusion_tag('components/article_tags.html', takes_context=True)
def article_tag_list(context):
    page = context['page']
    article_tags = page.tag.all()
    return {
        "request": context['request'],
        "article_tags": article_tags
    }