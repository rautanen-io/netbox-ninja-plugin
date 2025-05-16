from netbox.choices import ChoiceSet


class NinjaTemplateOutputTypeChoices(ChoiceSet):

    TEXT = "text"
    DRAW_IO = "drawio"
    JSON = "json"

    CHOICES = [
        (TEXT, "Text", "blue"),
        (DRAW_IO, "draw.io", "green"),
        (JSON, "JSON", "orange"),
    ]

    def get_text_display(self):
        return "black"
