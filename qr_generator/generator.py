import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer
)
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import io
from typing import Optional


class QRGenerator:
    def __init__(self):
        self.module_drawers = {
            'square': SquareModuleDrawer(),
            'gapped': GappedSquareModuleDrawer(),
            'circle': CircleModuleDrawer(),
            'rounded': RoundedModuleDrawer()
        }

    def hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def generate_qr(
            self,
            data: str,
            foreground_color: str = '#000000',
            background_color: str = '#FFFFFF',
            size: str = 'M',
            error_correction: str = 'M',
            module_style: str = 'square'
    ) -> io.BytesIO:
        try:
            fill_color = self.hex_to_rgb(foreground_color)
            back_color = self.hex_to_rgb(background_color)
        except Exception as e:
            print(f"Color conversion error: {e}, using defaults")
            fill_color = (0, 0, 0)
            back_color = (255, 255, 255)

        size_map = {'S': 4, 'M': 6, 'L': 8, 'XL': 10}
        box_size = size_map.get(size, 6)

        error_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        error_level = error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M)

        drawer = self.module_drawers.get(module_style, SquareModuleDrawer())

        qr = qrcode.QRCode(
            version=None,
            error_correction=error_level,
            box_size=box_size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        try:
            img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=SolidFillColorMask(
                    back_color=back_color,
                    front_color=fill_color
                ),
                module_drawer=drawer
            )
        except Exception as e:
            print(f"Styled image error: {e}, using basic image")
            img = qr.make_image(
                fill_color=fill_color,
                back_color=back_color
            )

        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)

        return bio

    def generate_svg(self, data: str) -> io.BytesIO:
        try:
            import segno
            qr = segno.make(data)
            bio = io.BytesIO()
            qr.save(bio, kind='svg', scale=8)
            bio.seek(0)
            return bio
        except ImportError:
            # Fallback to PNG if segno not available
            return self.generate_qr(data)

    def generate_eps(self, data: str) -> io.BytesIO:
        try:
            import segno
            qr = segno.make(data)
            bio = io.BytesIO()
            qr.save(bio, kind='eps')
            bio.seek(0)
            return bio
        except ImportError:
            # Fallback to PNG if segno not available
            return self.generate_qr(data)