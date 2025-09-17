from netbox.choices import ChoiceSet


class NinjaTemplateOutputTypeChoices(ChoiceSet):

    TEXT = "text"
    DRAW_IO = "drawio"
    JSON = "json"
    HTML = "html"

    CHOICES = [
        (TEXT, "Text", "blue"),
        (HTML, "HTML", "red"),
        (DRAW_IO, "draw.io", "green"),
        (JSON, "JSON", "orange"),
    ]

    def get_text_display(self):
        return "black"
