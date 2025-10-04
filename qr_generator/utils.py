import re
from datetime import datetime


class ValidationUtils:
    @staticmethod
    def validate_url(url: str) -> bool:
        pattern = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+'
            r'[A-Za-z]{2,6}'
            r'(:[0-9]{1,5})?'  # port
            r'(/.*)?$', re.IGNORECASE)
        return bool(pattern.match(url))

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        # Basic phone validation
        pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_hex_color(color: str) -> bool:
        pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        return bool(re.match(pattern, color))

    @staticmethod
    def validate_date(date_str: str) -> bool:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_time(time_str: str) -> bool:
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_coordinate(coord: str) -> bool:
        """Validate latitude/longitude coordinates"""
        try:
            value = float(coord)
            # Basic range validation
            return -180 <= value <= 180
        except ValueError:
            return False

    @staticmethod
    def validate_number(number: str) -> bool:
        """Validate if string is a number"""
        try:
            float(number)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_amount(amount: str) -> bool:
        """Validate payment amount"""
        try:
            value = float(amount)
            return value >= 0
        except ValueError:
            return False