import vobject
from datetime import datetime


class DataTemplates:
    @staticmethod
    def create_url(url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    @staticmethod
    def create_text(text: str) -> str:
        return text

    @staticmethod
    def create_email(address: str, subject: str = '', body: str = '') -> str:
        return f'mailto:{address}'

    @staticmethod
    def create_phone(phone: str) -> str:
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        return f'tel:{clean_phone}'

    @staticmethod
    def create_wifi(ssid: str, password: str = '', encryption: str = 'WPA') -> str:
        if encryption == 'nopass' or not password:
            return f'WIFI:T:nopass;S:{ssid};;'
        else:
            return f'WIFI:T:{encryption};S:{ssid};P:{password};;'

    @staticmethod
    def create_location(latitude: str, longitude: str) -> str:
        return f'geo:{latitude},{longitude}'

    @staticmethod
    def create_sms(phone: str, text: str = '') -> str:
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        if text:
            return f'smsto:{clean_phone}:{text}'
        else:
            return f'sms:{clean_phone}'

    @staticmethod
    def create_whatsapp(phone: str, text: str = '') -> str:
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        if text:
            # Remove + from phone number for WhatsApp
            clean_phone = clean_phone.replace('+', '')
            return f'https://wa.me/{clean_phone}?text={text}'
        else:
            clean_phone = clean_phone.replace('+', '')
            return f'https://wa.me/{clean_phone}'

    @staticmethod
    def create_vcard(name: str, company: str = '', phone: str = '',
                     email: str = '', website: str = '') -> str:
        try:
            vcard = vobject.vCard()
            vcard.add('n')
            vcard.n.value = vobject.vcard.Name(family=name, given=name)
            vcard.add('fn')
            vcard.fn.value = name

            if company:
                vcard.add('org')
                vcard.org.value = [company]

            if phone:
                vcard.add('tel')
                vcard.tel.value = phone
                vcard.tel.type_param = 'WORK'

            if email:
                vcard.add('email')
                vcard.email.value = email
                vcard.email.type_param = 'WORK'

            if website:
                vcard.add('url')
                vcard.url.value = website

            return vcard.serialize()
        except Exception as e:
            print(f"Error creating vCard: {e}")
            contact_info = f"Name: {name}"
            if company:
                contact_info += f"\nCompany: {company}"
            if phone:
                contact_info += f"\nPhone: {phone}"
            if email:
                contact_info += f"\nEmail: {email}"
            if website:
                contact_info += f"\nWebsite: {website}"
            return contact_info

    @staticmethod
    def create_event(title: str, date: str, time: str = '', location: str = '') -> str:
        try:
            # Format date for iCalendar
            date_str = date.replace('-', '')
            if time:
                datetime_str = f"{date_str}T{time.replace(':', '')}00"
            else:
                datetime_str = date_str

            ical = f"""BEGIN:VCALENDAR
                        VERSION:2.0
                        BEGIN:VEVENT
                        SUMMARY:{title}
                        DTSTART:{datetime_str}
                        LOCATION:{location}
                        END:VEVENT
                        END:VCALENDAR"""
            return ical
        except Exception as e:
            print(f"Error creating event: {e}")
            event_info = f"Event: {title}\nDate: {date}"
            if time:
                event_info += f"\nTime: {time}"
            if location:
                event_info += f"\nLocation: {location}"
            return event_info

    @staticmethod
    def create_paypal(email: str, amount: str = '') -> str:
        if amount:
            return f'https://paypal.me/{email}/{amount}'
        else:
            return f'https://paypal.me/{email}'

    @staticmethod
    def create_crypto(address: str, currency: str = 'BTC') -> str:
        currency_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether'
        }
        crypto_prefix = currency_map.get(currency, currency.lower())
        return f'{crypto_prefix}:{address}'

    @staticmethod
    def create_youtube(url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    @staticmethod
    def create_social(username: str, platform: str) -> str:
        platforms = {
            'instagram': f'https://instagram.com/{username}',
            'tiktok': f'https://tiktok.com/@{username}',
            'facebook': f'https://facebook.com/{username}',
            'linkedin': f'https://linkedin.com/in/{username}',
            'twitter': f'https://twitter.com/{username}'
        }
        return platforms.get(platform, f'https://{platform}.com/{username}')