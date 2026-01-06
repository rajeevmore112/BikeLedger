# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false


from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel 
from app.constants import POST_IT_YELLOW # pyright: ignore[reportUnusedImport]
from app.constants import POST_IT_GREEN # pyright: ignore[reportUnusedImport]

def entry_card(title, subtitle):
    title = str(title) if title else "No description"
    subtitle = str(subtitle) if subtitle else ""

    card = MDCard(
        padding=12,
        radius=[16],
        elevation=1,
        size_hint_y=None,
        height=72,
    )

    box = MDBoxLayout(orientation="vertical", spacing=2)

    box.add_widget(
        MDLabel(
            text=title,
            font_style="Subtitle1",
        )
    )

    if subtitle:
        box.add_widget(
            MDLabel(
                text=subtitle,
                font_style="Caption",
                theme_text_color="Secondary",
            )
        )

    card.add_widget(box)
    return card



def summary_card(title, on_release=None):
    kwargs = dict(
        padding=10,
        radius=[16],
        elevation=2,
        size_hint=(1, None),
        height=90,
        md_bg_color=(0.15, 0.18, 0.25, 1),
        
    )

    if on_release:
        kwargs["on_release"] = on_release

    card = MDCard(**kwargs)

    box = MDBoxLayout(orientation="vertical", spacing=4)

    box.add_widget(
        MDLabel(
            text=title,
            halign="center",
            theme_text_color="Secondary",
        )
    )

    value_label = MDLabel(
        text="₹0",
        halign="center",
        font_style="H6",
        theme_text_color="Custom",
        text_color=(0.90, 0.95, 1.00, 1),  # cool light blue
    )

    box.add_widget(value_label)
    card.add_widget(box)

    return card, value_label
