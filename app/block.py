from wagtail.blocks import StructBlock, CharBlock, RichTextBlock, StreamBlock, ListBlock
from wagtail.images.blocks import ImageChooserBlock

class ImageText(StructBlock):
    image1 = ImageChooserBlock()
    caption1 = CharBlock(max_length=100, required=False)
    image2 = ImageChooserBlock()
    caption2 = CharBlock(max_length=100, required=False)

class Quote(StructBlock):
    quote = RichTextBlock()
    author = CharBlock()

class BodyBlock(StreamBlock):
    heading = CharBlock()
    paragraph = RichTextBlock()
    image_carousel = ListBlock(ImageChooserBlock())
    bulleted_list = ListBlock(CharBlock())
    image_text = ImageText()
    quote = Quote()