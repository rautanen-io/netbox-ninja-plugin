from netbox.choices import ChoiceSet


class NinjaTemplateOutputTypeChoices(ChoiceSet):

    TEXT = "text"
    DRAW_IO = "drawio"

    CHOICES = [
        (TEXT, "Text", "blue"),
        (DRAW_IO, "draw.io", "green"),
    ]

    def get_text_display(self):
        return "black"
