# Layout config for responsive UI design in Main Window
from dataclasses import dataclass

BREAKPOINT_SMALL = 1024
BREAKPOINT_MEDIUM = 1366


@dataclass(frozen=True)
class LayoutConfig:
    """Responsive layout configuration."""

    width: int
    height: int
    sidebar_visible: bool
    margins: int
    spacing: int
    chat_padding: int
    sidebar_margin: int
    input_height: int
    button_width: int
    split_ratio: tuple[float, float]

    @classmethod
    def for_screen_width(cls, screen_width: int) -> "LayoutConfig":
        """Factory method to create config based on screen width."""
        if screen_width < BREAKPOINT_SMALL:
            return cls(
                width=min(900, int(screen_width * 0.9)),
                height=700,
                sidebar_visible=False,
                margins=20,
                spacing=16,
                chat_padding=20,
                sidebar_margin=15,
                input_height=52,
                button_width=120,
                split_ratio=(1.0, 0.0),
            )
        if screen_width < BREAKPOINT_MEDIUM:
            return cls(
                width=1100,
                height=750,
                sidebar_visible=True,
                margins=28,
                spacing=20,
                chat_padding=24,
                sidebar_margin=16,
                input_height=56,
                button_width=130,
                split_ratio=(0.72, 0.28),
            )
        return cls(
            width=1200,
            height=800,
            sidebar_visible=True,
            margins=32,
            spacing=24,
            chat_padding=28,
            sidebar_margin=18,
            input_height=60,
            button_width=140,
            split_ratio=(0.74, 0.26),
        )
