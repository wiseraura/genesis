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
from django.core.paginator import PageNotAnInteger,EmptyPage,Paginator
from datetime import datetime
from django.http import Http404
from django.utils.functional import cached_property
from wagtail.search import index
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField


class Home(RoutablePageMixin, Page):
    description = models.CharField(max_length=500, blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['home'] = self
        pagenator = Paginator(self.articles,2)
        page = request.GET.get('page')
        try:
            articles = pagenator.page(page)
        except PageNotAnInteger:
            articles = pagenator.page(1)
        except EmptyPage:
            articles = pagenator.object_list.none()    
        context['articles'] = articles
        return context

    def get_articles(self):
        return Article.objects.descendant_of(self).live().order_by("-post_date")
    
    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.articles = self.get_articles().filter(post_date__year = year)
        if month:
            self.articles = self.articles.filter(post_date__month = month)
        if day:
            self.articles = self.articles.filter(post_date__day = day)
        return self.render(request)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_name(self, request, year, month, day, slug, *args, **kwargs):
        article = self.get_articles().filter(slug = slug).first()
        if not article:
            raise Http404
        return article.serve(request)


    @route(r'^tag/(?P<tag>[\w-]+)/$')
    def post_by_tag(self, request, tag):
        self.articles = self.get_articles().filter(tag__name = tag)
        return self.render(request)
    
    @route(r'^category/(?P<category>[\w-]+)/$')
    def post_by_category(self, request, category):
        self.articles = self.get_articles().filter(categories__category__name = category)
        return self.render(request)
    
    @route(r'^$')
    def all_articles(self, request):
        self.articles = self.get_articles()
        return self.render(request)
    
    @route(r'search/$')
    def search(self, request):
        search_query = request.GET.get('q', None)
        self.articles = self.get_articles()
        if search_query:
            self.articles = self.articles.search(search_query)
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
    post_date = models.DateTimeField(verbose_name="post date", default=datetime.today)
    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("tag"),
        InlinePanel("categories", label="category"),
        FieldPanel("body"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("post_date")
    ]
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('title'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['home'] = self.home
        return context

    @cached_property
    def home(self):
        return self.get_parent().specific

    @cached_property
    def canonical_url(self):
        from .templatetags.templates_tags import article_date_name_url
        home = self.home
        return article_date_name_url(self, home)


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


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class FormPage(AbstractForm):
    content_panels = AbstractForm.content_panels + [
        InlinePanel("form_fields", label="Form Fields"),
    ]

    @cached_property
    def home(self):
        return self.get_parent().specific
    
    def get_context(self, request, *args, **kwargs):
        context = super(FormPage, self).get_context(request, *args, **kwargs)
        context['home'] = self.home
        return context