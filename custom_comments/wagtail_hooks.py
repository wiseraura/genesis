from . import get_model as get_comment_model
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html, strip_tags
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register


class CommentAdmin(ModelAdmin):
    model = get_comment_model()
    menu_label = "comments"
    menu_icon = "doc-full-inverse"
    add_to_settings_menu = False
    list_display = (
        "plain_text_comment",
        "name",
        "submit_date",
        "comment_page_type",
        "comment_page",
    )
    ordering = ("-submit_date",)
    search_fields = "comment"
    list_per_page = 10
    form_fields_exclude = [
        "submit_date",
        "ip_adress",
        "is_removed",
        "is_public",
        "user_url",
        "user",
        "content_type",
        "object_pk",
        "content_object",
        "site",
    ]

    def comment_page_type(self, obj):
        ct = ContentType.objects.get(pk=obj.content_object.content_type_id)
        return ct.model_class().__name__
    
    def comment_page(self, obj):
        return format_html(
            f"<a href='{obj.content_object.specific.url}'>{ obj.content_object.specific.title }</a>"
        )
    
    def plain_text_comment(self, obj):
        return strip_tags(obj.comment)
    

modeladmin_register(CommentAdmin)