from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from taggit.models import Tag as TaggitTag
from modelcluster.models import ParentalKey
from taggit.models import TaggedItemBase
from modelcluster.tags import ClusterTaggableManager
from .block import BodyBlock
from wagtail.fields import StreamField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

class Home(RoutablePageMixin, Page):
    description = models.CharField(max_length=500, blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['home'] = self
        context['articles'] = self.articles
        return context

    def get_articles(self):
        return Article.objects.descendant_of(self).live()
    
    @route(r'^tag/(?P<tag>[\w-]+)/$')
    def post_by_tag(self, request, tag):
        self.articles = self.get_articles().filter(tag__name = tag)
        return self.render(request)
    
    @route(r'^category/(?P<category>[\w-]+)/$')
    def post_by_category(self, request, category):
        self.articles = self.get_articles().filter(category__category__name = category)
        return self.render(request)
    
    @route(r'^$')
    def all_articles(self, request):
        self.articles = self.get_articles()
        return self.render(request)

class Article(Page):
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tag = ClusterTaggableManager(through='ArticleTag', blank=True)
    body = StreamField(BodyBlock(), blank=True, use_json_field=True)
    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("tag"),
        InlinePanel("categories", label="category"),
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['article'] = self.get_parent().specific
        return context

class ArticleCategory(models.Model):
    page = ParentalKey(
        "app.Article",
        on_delete=models.CASCADE,
        blank=True,
        related_name="categories"
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="post_pages"
    )

    panel = [
        FieldPanel('category'),
    ]

    class Meta:
        unique_together = (('page', 'category'))

class ArticleTag(TaggedItemBase):
    content_object = ParentalKey(
        "Article", 
        blank=True, 
        related_name='article_tag'
    )

@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(max_length=250, unique=True)

    panel = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True