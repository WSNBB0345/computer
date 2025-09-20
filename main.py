"""Entry point for running the desktop pet."""
from __future__ import annotations

from desktop_pet import DesktopPetApp


def main() -> None:
    app = DesktopPetApp()
    app.run()


if __name__ == "__main__":
    main()
