MOD_CATEGORIES = [
    "Accessories",
    "Brakes & Clutch",
    "Tyres",
    "Luggage",
    "Aesthetic",
    "Essential Components",
]

APP_BG = (0.055, 0.07, 0.09, 1)
SURFACE = (0.10, 0.13, 0.17, 1)
SURFACE_ALT = (0.13, 0.17, 0.22, 1)
TEXT_PRIMARY = (0.94, 0.96, 0.98, 1)
TEXT_MUTED = (0.62, 0.68, 0.74, 1)
ACCENT_TEAL = (0.0, 0.78, 0.69, 1)
ACCENT_AMBER = (1.0, 0.68, 0.22, 1)
ACCENT_RED = (1.0, 0.34, 0.34, 1)

CATEGORY_STYLES = {
    "Accessories": {
        "icon": "toolbox-outline",
        "color": (0.0, 0.70, 0.82, 1),
        "bg": (0.07, 0.20, 0.25, 1),
    },
    "Brakes & Clutch": {
        "icon": "car-brake-alert",
        "color": (1.0, 0.50, 0.36, 1),
        "bg": (0.25, 0.12, 0.11, 1),
    },
    "Tyres": {
        "icon": "tire",
        "color": (0.55, 0.82, 0.36, 1),
        "bg": (0.13, 0.22, 0.13, 1),
    },
    "Luggage": {
        "icon": "bag-suitcase-outline",
        "color": (0.72, 0.56, 1.0, 1),
        "bg": (0.18, 0.14, 0.27, 1),
    },
    "Aesthetic": {
        "icon": "palette-outline",
        "color": (1.0, 0.56, 0.78, 1),
        "bg": (0.25, 0.12, 0.19, 1),
    },
    "Essential Components": {
        "icon": "engine-outline",
        "color": (1.0, 0.72, 0.25, 1),
        "bg": (0.25, 0.18, 0.08, 1),
    },
}


def category_style(category):
    return CATEGORY_STYLES.get(
        category,
        {
            "icon": "wrench-outline",
            "color": ACCENT_TEAL,
            "bg": SURFACE_ALT,
        },
    )
