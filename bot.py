import os
import json
from typing import Dict, Any
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import BOT_TOKEN, LOCALES_DIR, DEFAULT_LANGUAGE
from qr_generator.generator import QRGenerator
from qr_generator.templates import DataTemplates
from qr_generator.utils import ValidationUtils


class Localization:
    def __init__(self, locales_dir: str = LOCALES_DIR):
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, str]] = {}
        self.available_languages = {}
        self.load_all_locales()

    def load_all_locales(self):
        """Dynamically load all locale files from locales directory"""
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir)
            print(f"Created locales directory: {self.locales_dir}")
            return

        for filename in os.listdir(self.locales_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.locales_dir, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations = json.load(f)

                    self.translations[lang_code] = translations

                    # Get language name from the file or use code as fallback
                    lang_name = translations.get('language_name', lang_code)
                    self.available_languages[lang_code] = lang_name

                    print(f"Loaded locale: {lang_code} - {lang_name}")

                except Exception as e:
                    print(f"Error loading locale {filename}: {e}")

    def get_text(self, lang_code: str, key: str) -> str:
        """Get translated text for given language and key"""
        if lang_code not in self.translations:
            # Fallback to default language
            lang_code = DEFAULT_LANGUAGE

        if lang_code in self.translations:
            return self.translations[lang_code].get(key, f"[{key}]")

        return f"[{key}]"

    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available language codes and names"""
        return self.available_languages


class QRBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.loc = Localization()
        self.qr_generator = QRGenerator()
        self.data_templates = DataTemplates()
        self.validation = ValidationUtils()
        self.setup_handlers()

    def get_user_lang(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        return context.user_data.get('language', DEFAULT_LANGUAGE)

    # Dynamic keyboard methods that use localization
    def create_main_menu_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.loc.get_text(lang, "create_qr")],
            [self.loc.get_text(lang, "help")],
            [self.loc.get_text(lang, "language")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_data_type_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        # Data types are now defined in localization files
        data_types = [
            self.loc.get_text(lang, "data_type_url"),
            self.loc.get_text(lang, "data_type_text"),
            self.loc.get_text(lang, "data_type_email"),
            self.loc.get_text(lang, "data_type_phone"),
            self.loc.get_text(lang, "data_type_wifi"),
            self.loc.get_text(lang, "data_type_location"),
            self.loc.get_text(lang, "data_type_sms"),
            self.loc.get_text(lang, "data_type_whatsapp"),
            self.loc.get_text(lang, "data_type_vcard"),
            self.loc.get_text(lang, "data_type_event"),
            self.loc.get_text(lang, "data_type_paypal"),
            self.loc.get_text(lang, "data_type_crypto"),
            self.loc.get_text(lang, "data_type_youtube"),
            self.loc.get_text(lang, "data_type_social")
        ]

        keyboard = []
        for i in range(0, len(data_types), 2):
            row = data_types[i:i + 2]
            keyboard.append(row)

        keyboard.append([self.loc.get_text(lang, "back")])
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_cancel_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [[self.loc.get_text(lang, "cancel")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_language_keyboard(self) -> ReplyKeyboardMarkup:
        """Create language selection keyboard dynamically from available locales"""
        languages = self.loc.get_available_languages()
        keyboard = []

        # Convert to list of language names
        lang_names = list(languages.values())

        # Create rows with 2 buttons each
        for i in range(0, len(lang_names), 2):
            row = lang_names[i:i + 2]
            keyboard.append(row)

        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_encryption_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.loc.get_text(lang, "encryption_wpa"), self.loc.get_text(lang, "encryption_wep")],
            [self.loc.get_text(lang, "encryption_none")],
            [self.loc.get_text(lang, "cancel")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_crypto_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.loc.get_text(lang, "crypto_btc")],
            [self.loc.get_text(lang, "crypto_eth")],
            [self.loc.get_text(lang, "crypto_usdt")],
            [self.loc.get_text(lang, "back")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_social_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.loc.get_text(lang, "social_instagram"), self.loc.get_text(lang, "social_tiktok")],
            [self.loc.get_text(lang, "social_facebook"), self.loc.get_text(lang, "social_linkedin")],
            [self.loc.get_text(lang, "social_twitter")],
            [self.loc.get_text(lang, "back")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def create_skip_keyboard(self, lang: str) -> ReplyKeyboardMarkup:
        keyboard = [
            [self.loc.get_text(lang, "skip")],
            [self.loc.get_text(lang, "cancel")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("new", self.new_qr))
        self.application.add_handler(CommandHandler("cancel", self.cancel))

        # Dynamic handlers for all text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_dynamic_text))

    async def handle_dynamic_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages dynamically based on current language"""
        user_text = update.message.text
        lang = self.get_user_lang(context)

        # Get current language texts
        create_qr_text = self.loc.get_text(lang, "create_qr")
        help_text = self.loc.get_text(lang, "help")
        language_text = self.loc.get_text(lang, "language")
        back_text = self.loc.get_text(lang, "back")
        cancel_text = self.loc.get_text(lang, "cancel")
        skip_text = self.loc.get_text(lang, "skip")

        # Check for WiFi multi-step input first
        if 'wifi_data' in context.user_data:
            return await self.handle_wifi_input(update, context, user_text)

        # Check for multi-step input for location, sms, whatsapp, etc.
        if 'multi_step_data' in context.user_data:
            return await self.handle_multi_step_input(update, context, user_text)

        # Main menu handlers
        if user_text == create_qr_text:
            return await self.create_qr(update, context)
        elif user_text == help_text:
            return await self.help_command(update, context)
        elif user_text == language_text:
            return await self.language_command(update, context)

        # Data type selection
        elif user_text in [
            self.loc.get_text(lang, "data_type_url"),
            self.loc.get_text(lang, "data_type_text"),
            self.loc.get_text(lang, "data_type_email"),
            self.loc.get_text(lang, "data_type_phone"),
            self.loc.get_text(lang, "data_type_wifi"),
            self.loc.get_text(lang, "data_type_location"),
            self.loc.get_text(lang, "data_type_sms"),
            self.loc.get_text(lang, "data_type_whatsapp"),
            self.loc.get_text(lang, "data_type_vcard"),
            self.loc.get_text(lang, "data_type_event"),
            self.loc.get_text(lang, "data_type_paypal"),
            self.loc.get_text(lang, "data_type_crypto"),
            self.loc.get_text(lang, "data_type_youtube"),
            self.loc.get_text(lang, "data_type_social")
        ]:
            return await self.handle_data_type_selection(update, context, user_text)

        # Navigation
        elif user_text == back_text:
            return await self.show_main_menu(update, context)
        elif user_text == cancel_text:
            return await self.cancel_operation(update, context)

        # Language selection (check all available languages)
        elif user_text in self.loc.get_available_languages().values():
            return await self.handle_language_selection(update, context, user_text)

        # Encryption selection for WiFi
        elif user_text in [
            self.loc.get_text(lang, "encryption_wpa"),
            self.loc.get_text(lang, "encryption_wep"),
            self.loc.get_text(lang, "encryption_none")
        ]:
            return await self.handle_wifi_encryption(update, context, user_text)

        # Crypto selection
        elif user_text in [
            self.loc.get_text(lang, "crypto_btc"),
            self.loc.get_text(lang, "crypto_eth"),
            self.loc.get_text(lang, "crypto_usdt")
        ]:
            return await self.handle_crypto_selection(update, context, user_text)

        # Social media selection
        elif user_text in [
            self.loc.get_text(lang, "social_instagram"),
            self.loc.get_text(lang, "social_tiktok"),
            self.loc.get_text(lang, "social_facebook"),
            self.loc.get_text(lang, "social_linkedin"),
            self.loc.get_text(lang, "social_twitter")
        ]:
            return await self.handle_social_selection(update, context, user_text)

        # Skip option
        elif user_text == skip_text:
            return await self.handle_skip_input(update, context)

        # Data input for QR generation (single step)
        elif 'current_data_type' in context.user_data:
            return await self.handle_single_input(update, context, user_text)

        # Unknown input
        else:
            await update.message.reply_text(
                self.loc.get_text(lang, "use_buttons"),
                reply_markup=self.create_main_menu_keyboard(lang)
            )

    async def handle_data_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
        """Handle data type selection dynamically"""
        lang = self.get_user_lang(context)

        # Map localized text to data type
        data_type_map = {
            self.loc.get_text(lang, "data_type_url"): 'url',
            self.loc.get_text(lang, "data_type_text"): 'text',
            self.loc.get_text(lang, "data_type_email"): 'email',
            self.loc.get_text(lang, "data_type_phone"): 'phone',
            self.loc.get_text(lang, "data_type_wifi"): 'wifi',
            self.loc.get_text(lang, "data_type_location"): 'location',
            self.loc.get_text(lang, "data_type_sms"): 'sms',
            self.loc.get_text(lang, "data_type_whatsapp"): 'whatsapp',
            self.loc.get_text(lang, "data_type_vcard"): 'vcard',
            self.loc.get_text(lang, "data_type_event"): 'event',
            self.loc.get_text(lang, "data_type_paypal"): 'paypal',
            self.loc.get_text(lang, "data_type_crypto"): 'crypto',
            self.loc.get_text(lang, "data_type_youtube"): 'youtube',
            self.loc.get_text(lang, "data_type_social"): 'social'
        }

        data_type = data_type_map.get(user_text)
        if data_type:
            context.user_data['current_data_type'] = data_type

            if data_type == 'wifi':
                context.user_data['wifi_data'] = {'step': 'ssid'}
                await update.message.reply_text(
                    self.loc.get_text(lang, "enter_wifi_ssid"),
                    reply_markup=self.create_cancel_keyboard(lang)
                )
            elif data_type in ['location', 'sms', 'whatsapp', 'vcard', 'event', 'paypal', 'crypto', 'social']:
                # Multi-step inputs for these types
                context.user_data['multi_step_data'] = {
                    'type': data_type,
                    'step': 1,
                    'inputs': {}
                }
                await self.ask_for_multi_step_input(update, context)
            else:
                # Single input types
                prompt_key = f"enter_{data_type}"
                await update.message.reply_text(
                    self.loc.get_text(lang, prompt_key),
                    reply_markup=self.create_cancel_keyboard(lang)
                )

    async def ask_for_multi_step_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for next input in multi-step data entry"""
        lang = self.get_user_lang(context)
        multi_data = context.user_data.get('multi_step_data', {})
        data_type = multi_data.get('type')
        step = multi_data.get('step', 1)

        prompts = {
            'location': {
                1: self.loc.get_text(lang, "enter_location_lat"),
                2: self.loc.get_text(lang, "enter_location_lon")
            },
            'sms': {
                1: self.loc.get_text(lang, "enter_sms_phone"),
                2: self.loc.get_text(lang, "enter_sms_text")
            },
            'whatsapp': {
                1: self.loc.get_text(lang, "enter_whatsapp_phone"),
                2: self.loc.get_text(lang, "enter_whatsapp_text")
            },
            'vcard': {
                1: self.loc.get_text(lang, "enter_vcard_name"),
                2: self.loc.get_text(lang, "enter_vcard_company"),
                3: self.loc.get_text(lang, "enter_vcard_phone"),
                4: self.loc.get_text(lang, "enter_vcard_email"),
                5: self.loc.get_text(lang, "enter_vcard_website")
            },
            'event': {
                1: self.loc.get_text(lang, "enter_event_title"),
                2: self.loc.get_text(lang, "enter_event_date"),
                3: self.loc.get_text(lang, "enter_event_time"),
                4: self.loc.get_text(lang, "enter_event_location")
            },
            'paypal': {
                1: self.loc.get_text(lang, "enter_paypal_email"),
                2: self.loc.get_text(lang, "enter_paypal_amount")
            }
        }

        if data_type in prompts and step in prompts[data_type]:
            # For optional fields in vcard and event, show skip button
            if data_type in ['vcard', 'event'] and step >= 2:
                await update.message.reply_text(
                    f"{prompts[data_type][step]} {self.loc.get_text(lang, 'optional')}",
                    reply_markup=self.create_skip_keyboard(lang)
                )
            elif data_type == 'paypal' and step == 2:
                await update.message.reply_text(
                    f"{prompts[data_type][step]} {self.loc.get_text(lang, 'optional')}",
                    reply_markup=self.create_skip_keyboard(lang)
                )
            else:
                await update.message.reply_text(
                    prompts[data_type][step],
                    reply_markup=self.create_cancel_keyboard(lang)
                )
        elif data_type == 'crypto' and step == 1:
            await update.message.reply_text(
                self.loc.get_text(lang, "enter_crypto_address"),
                reply_markup=self.create_cancel_keyboard(lang)
            )
        elif data_type == 'crypto' and step == 2:
            await update.message.reply_text(
                self.loc.get_text(lang, "enter_crypto_currency"),
                reply_markup=self.create_crypto_keyboard(lang)
            )
        elif data_type == 'social' and step == 1:
            await update.message.reply_text(
                self.loc.get_text(lang, "enter_social_username"),
                reply_markup=self.create_cancel_keyboard(lang)
            )
        elif data_type == 'social' and step == 2:
            await update.message.reply_text(
                self.loc.get_text(lang, "enter_social_platform"),
                reply_markup=self.create_social_keyboard(lang)
            )

    async def handle_multi_step_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
        """Handle multi-step data input"""
        lang = self.get_user_lang(context)
        multi_data = context.user_data.get('multi_step_data', {})
        data_type = multi_data.get('type')
        step = multi_data.get('step', 1)

        # Check for skip
        if user_text == self.loc.get_text(lang, "skip"):
            multi_data['inputs'][step] = ''  # Store empty for skipped field
        # Check for cancel
        elif user_text == self.loc.get_text(lang, "cancel"):
            return await self.cancel_operation(update, context)
        else:
            # Validate input based on step and data type
            if not await self.validate_multi_step_input(update, context, user_text, data_type, step):
                return

            # Store the input
            multi_data['inputs'][step] = user_text

        # Check if we need more inputs
        total_steps = {
            'location': 2,
            'sms': 2,
            'whatsapp': 2,
            'vcard': 5,
            'event': 4,
            'paypal': 2,
            'crypto': 2,
            'social': 2
        }

        if step < total_steps.get(data_type, 1):
            # Ask for next input
            multi_data['step'] = step + 1
            await self.ask_for_multi_step_input(update, context)
        else:
            # All inputs collected, generate QR code
            inputs = multi_data['inputs']
            qr_data = self.generate_multi_step_qr_data(data_type, inputs)

            if qr_data:
                await self.generate_and_send_qr(update, context, qr_data)
            else:
                await update.message.reply_text(
                    "❌ Ошибка генерации данных",
                    reply_markup=self.create_main_menu_keyboard(lang)
                )

            # Clean up
            context.user_data.pop('multi_step_data', None)
            context.user_data.pop('current_data_type', None)

            # Return to main menu
            await update.message.reply_text(
                self.loc.get_text(lang, "qr_ready"),
                reply_markup=self.create_main_menu_keyboard(lang)
            )

    async def validate_multi_step_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                        user_input: str, data_type: str, step: int) -> bool:
        """Validate multi-step input"""
        lang = self.get_user_lang(context)

        validation_rules = {
            'location': {
                1: ('coordinate', self.loc.get_text(lang, "invalid_coordinate")),
                2: ('coordinate', self.loc.get_text(lang, "invalid_coordinate"))
            },
            'sms': {
                1: ('phone', self.loc.get_text(lang, "invalid_phone")),
                2: ('text', None)
            },
            'whatsapp': {
                1: ('phone', self.loc.get_text(lang, "invalid_phone")),
                2: ('text', None)
            },
            'vcard': {
                1: ('required', "Имя обязательно"),
                2: ('optional', None),
                3: ('phone_optional', None),
                4: ('email_optional', None),
                5: ('url_optional', None)
            },
            'event': {
                1: ('required', "Название обязательно"),
                2: ('date', self.loc.get_text(lang, "invalid_date")),
                3: ('time_optional', None),
                4: ('optional', None)
            },
            'paypal': {
                1: ('email', self.loc.get_text(lang, "invalid_email")),
                2: ('amount_optional', None)
            },
            'crypto': {
                1: ('required', "Адрес обязателен"),
            },
            'social': {
                1: ('required', "Username обязателен"),
            }
        }

        if data_type in validation_rules and step in validation_rules[data_type]:
            validation_type, error_message = validation_rules[data_type][step]

            if validation_type == 'required' and not user_input.strip():
                await update.message.reply_text(error_message)
                return False
            elif validation_type == 'phone' and not self.validation.validate_phone(user_input):
                await update.message.reply_text(error_message)
                return False
            elif validation_type == 'phone_optional' and user_input.strip() and not self.validation.validate_phone(
                    user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_phone"))
                return False
            elif validation_type == 'email' and not self.validation.validate_email(user_input):
                await update.message.reply_text(error_message)
                return False
            elif validation_type == 'email_optional' and user_input.strip() and not self.validation.validate_email(
                    user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_email"))
                return False
            elif validation_type == 'coordinate' and not self.validation.validate_coordinate(user_input):
                await update.message.reply_text(error_message)
                return False
            elif validation_type == 'date' and not self.validation.validate_date(user_input):
                await update.message.reply_text(error_message)
                return False
            elif validation_type == 'time_optional' and user_input.strip() and not self.validation.validate_time(
                    user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_time"))
                return False
            elif validation_type == 'amount_optional' and user_input.strip() and not self.validation.validate_amount(
                    user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_number"))
                return False
            elif validation_type == 'url_optional' and user_input.strip() and not self.validation.validate_url(
                    user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_url"))
                return False

        return True

    def generate_multi_step_qr_data(self, data_type: str, inputs: dict) -> str:
        """Generate QR code data for multi-step inputs"""
        try:
            if data_type == 'location':
                return self.data_templates.create_location(
                    inputs[1],  # latitude
                    inputs[2]  # longitude
                )
            elif data_type == 'sms':
                return self.data_templates.create_sms(
                    inputs[1],  # phone
                    inputs.get(2, '')  # text
                )
            elif data_type == 'whatsapp':
                return self.data_templates.create_whatsapp(
                    inputs[1],  # phone
                    inputs.get(2, '')  # text
                )
            elif data_type == 'vcard':
                return self.data_templates.create_vcard(
                    inputs[1],  # name
                    inputs.get(2, ''),  # company
                    inputs.get(3, ''),  # phone
                    inputs.get(4, ''),  # email
                    inputs.get(5, '')  # website
                )
            elif data_type == 'event':
                return self.data_templates.create_event(
                    inputs[1],  # title
                    inputs[2],  # date
                    inputs.get(3, ''),  # time
                    inputs.get(4, '')  # location
                )
            elif data_type == 'paypal':
                return self.data_templates.create_paypal(
                    inputs[1],  # email
                    inputs.get(2, '')  # amount
                )
            elif data_type == 'crypto':
                currency = inputs.get(2, 'BTC')
                return self.data_templates.create_crypto(
                    inputs[1],  # address
                    currency
                )
            elif data_type == 'social':
                platform = inputs.get(2, 'instagram')
                return self.data_templates.create_social(
                    inputs[1],  # username
                    platform
                )
            elif data_type == 'youtube':
                return self.data_templates.create_youtube(inputs[1])
        except Exception as e:
            print(f"Error generating multi-step QR data: {e}")

        return ""

    async def handle_single_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
        """Handle single input data types"""
        lang = self.get_user_lang(context)
        data_type = context.user_data.get('current_data_type')

        # Validate input
        if not await self.validate_input(update, context, user_text, data_type):
            return

        # Generate QR data
        qr_data = self.generate_qr_data(data_type, user_text)
        if not qr_data:
            await update.message.reply_text(
                "❌ Ошибка генерации данных",
                reply_markup=self.create_main_menu_keyboard(lang)
            )
            return

        # Generate and send QR code
        await self.generate_and_send_qr(update, context, qr_data)

        # Clear current data type
        context.user_data.pop('current_data_type', None)

        # Return to main menu
        await update.message.reply_text(
            self.loc.get_text(lang, "qr_ready"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def validate_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                             user_input: str, data_type: str) -> bool:
        """Validate user input"""
        lang = self.get_user_lang(context)

        if data_type == 'url':
            if not self.validation.validate_url(user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_url"))
                return False
        elif data_type == 'email':
            if not self.validation.validate_email(user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_email"))
                return False
        elif data_type == 'text':
            if len(user_input) > 500:
                await update.message.reply_text(self.loc.get_text(lang, "text_too_long"))
                return False
        elif data_type == 'phone':
            if not self.validation.validate_phone(user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_phone"))
                return False
        elif data_type == 'youtube':
            if not self.validation.validate_url(user_input):
                await update.message.reply_text(self.loc.get_text(lang, "invalid_url"))
                return False

        return True

    def generate_qr_data(self, data_type: str, user_input: str) -> str:
        """Generate QR code data string for single-input types"""
        try:
            if data_type == 'url':
                return self.data_templates.create_url(user_input)
            elif data_type == 'text':
                return self.data_templates.create_text(user_input)
            elif data_type == 'email':
                return self.data_templates.create_email(user_input)
            elif data_type == 'phone':
                return self.data_templates.create_phone(user_input)
            elif data_type == 'youtube':
                return self.data_templates.create_youtube(user_input)
            # WiFi, location, sms, whatsapp, vcard, event, paypal, crypto, social handled separately
            else:
                return user_input
        except Exception as e:
            print(f"Error generating QR data: {e}")
            return user_input

    async def generate_and_send_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Generate and send QR code"""
        lang = self.get_user_lang(context)

        if not data or data.strip() == "":
            await update.message.reply_text("❌ Ошибка: пустые данные для QR-кода")
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')

        # Show generating message
        generating_msg = await update.message.reply_text(self.loc.get_text(lang, "generating_qr"))

        try:
            # Generate QR code
            qr_image = self.qr_generator.generate_qr(data)

            # Send QR code
            await update.message.reply_photo(
                photo=qr_image,
                caption=self.loc.get_text(lang, "qr_ready")
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка генерации QR-кода: {str(e)}")
        finally:
            # Delete generating message
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=generating_msg.message_id
                )
            except:
                pass

    async def handle_wifi_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
        """Handle multi-step WiFi input"""
        wifi_data = context.user_data['wifi_data']
        current_step = wifi_data.get('step')
        lang = self.get_user_lang(context)

        cancel_text = self.loc.get_text(lang, "cancel")
        if user_text == cancel_text:
            context.user_data.pop('wifi_data', None)
            context.user_data.pop('current_data_type', None)
            await update.message.reply_text(
                self.loc.get_text(lang, "operation_cancelled"),
                reply_markup=self.create_main_menu_keyboard(lang)
            )
            return

        if current_step == 'ssid':
            # Store SSID and ask for encryption type
            wifi_data['ssid'] = user_text
            wifi_data['step'] = 'encryption'
            await update.message.reply_text(
                self.loc.get_text(lang, "select_encryption"),
                reply_markup=self.create_encryption_keyboard(lang)
            )

        elif current_step == 'password':
            # Store password and generate QR
            wifi_data['password'] = user_text
            wifi_data['step'] = 'final'
            await self.finalize_wifi_qr(update, context)

    async def handle_wifi_encryption(self, update: Update, context: ContextTypes.DEFAULT_TYPE, encryption_text: str):
        """Handle WiFi encryption selection"""
        lang = self.get_user_lang(context)
        wifi_data = context.user_data.get('wifi_data', {})

        encryption_map = {
            self.loc.get_text(lang, "encryption_wpa"): 'WPA',
            self.loc.get_text(lang, "encryption_wep"): 'WEP',
            self.loc.get_text(lang, "encryption_none"): 'nopass'
        }

        encryption = encryption_map.get(encryption_text, 'WPA')
        wifi_data['encryption'] = encryption

        if encryption == 'nopass':
            wifi_data['step'] = 'final'
            await self.finalize_wifi_qr(update, context)
        else:
            wifi_data['step'] = 'password'
            await update.message.reply_text(
                self.loc.get_text(lang, "enter_wifi_password"),
                reply_markup=self.create_cancel_keyboard(lang)
            )

    async def finalize_wifi_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finalize WiFi QR code generation"""
        wifi_data = context.user_data['wifi_data']
        lang = self.get_user_lang(context)

        # Generate QR data using the template
        try:
            qr_data = self.data_templates.create_wifi(
                wifi_data['ssid'],
                wifi_data.get('password', ''),
                wifi_data.get('encryption', 'WPA')
            )
        except Exception as e:
            print(f"Error generating WiFi QR data: {e}")
            await update.message.reply_text(
                "❌ Ошибка генерации WiFi данных",
                reply_markup=self.create_main_menu_keyboard(lang)
            )
            return

        if not qr_data:
            await update.message.reply_text(
                "❌ Ошибка генерации WiFi данных",
                reply_markup=self.create_main_menu_keyboard(lang)
            )
            return

        # Generate and send QR code
        await self.generate_and_send_qr(update, context, qr_data)

        # Clear WiFi data
        context.user_data.pop('wifi_data', None)
        context.user_data.pop('current_data_type', None)

        # Return to main menu
        await update.message.reply_text(
            self.loc.get_text(lang, "qr_ready"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def handle_crypto_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, crypto_text: str):
        """Handle cryptocurrency selection"""
        lang = self.get_user_lang(context)
        multi_data = context.user_data.get('multi_step_data', {})

        crypto_map = {
            self.loc.get_text(lang, "crypto_btc"): 'BTC',
            self.loc.get_text(lang, "crypto_eth"): 'ETH',
            self.loc.get_text(lang, "crypto_usdt"): 'USDT'
        }

        currency = crypto_map.get(crypto_text, 'BTC')
        multi_data['inputs'][2] = currency
        multi_data['step'] = 3  # Mark as complete

        # Generate QR code
        inputs = multi_data['inputs']
        qr_data = self.generate_multi_step_qr_data('crypto', inputs)

        if qr_data:
            await self.generate_and_send_qr(update, context, qr_data)

        # Clean up
        context.user_data.pop('multi_step_data', None)
        context.user_data.pop('current_data_type', None)

        await update.message.reply_text(
            self.loc.get_text(lang, "qr_ready"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def handle_social_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, social_text: str):
        """Handle social media platform selection"""
        lang = self.get_user_lang(context)
        multi_data = context.user_data.get('multi_step_data', {})

        social_map = {
            self.loc.get_text(lang, "social_instagram"): 'instagram',
            self.loc.get_text(lang, "social_tiktok"): 'tiktok',
            self.loc.get_text(lang, "social_facebook"): 'facebook',
            self.loc.get_text(lang, "social_linkedin"): 'linkedin',
            self.loc.get_text(lang, "social_twitter"): 'twitter'
        }

        platform = social_map.get(social_text, 'instagram')
        multi_data['inputs'][2] = platform
        multi_data['step'] = 3  # Mark as complete

        # Generate QR code
        inputs = multi_data['inputs']
        qr_data = self.generate_multi_step_qr_data('social', inputs)

        if qr_data:
            await self.generate_and_send_qr(update, context, qr_data)

        # Clean up
        context.user_data.pop('multi_step_data', None)
        context.user_data.pop('current_data_type', None)

        await update.message.reply_text(
            self.loc.get_text(lang, "qr_ready"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def handle_skip_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle skip input"""
        return await self.handle_multi_step_input(update, context,
                                                  self.loc.get_text(self.get_user_lang(context), "skip"))

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language_name: str):
        """Handle language selection dynamically"""
        # Find language code by name
        languages = self.loc.get_available_languages()
        for lang_code, name in languages.items():
            if name == language_name:
                context.user_data['language'] = lang_code
                await update.message.reply_text(
                    self.loc.get_text(lang_code, "language_changed"),
                    reply_markup=self.create_main_menu_keyboard(lang_code)
                )
                return

        # Fallback to default if not found
        context.user_data['language'] = DEFAULT_LANGUAGE
        await update.message.reply_text(
            self.loc.get_text(DEFAULT_LANGUAGE, "language_changed"),
            reply_markup=self.create_main_menu_keyboard(DEFAULT_LANGUAGE)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        lang = self.get_user_lang(context)

        await update.message.reply_text(
            self.loc.get_text(lang, "welcome"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        lang = self.get_user_lang(context)
        await update.message.reply_text(
            self.loc.get_text(lang, "main_menu"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def create_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start QR creation process"""
        lang = self.get_user_lang(context)

        # Clear previous data
        context.user_data.pop('current_data_type', None)
        context.user_data.pop('qr_data', None)
        context.user_data.pop('wifi_data', None)
        context.user_data.pop('multi_step_data', None)

        await update.message.reply_text(
            self.loc.get_text(lang, "select_data_type"),
            reply_markup=self.create_data_type_keyboard(lang)
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        lang = self.get_user_lang(context)
        await update.message.reply_text(
            self.loc.get_text(lang, "help_text"),
            parse_mode='Markdown',
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Change language"""
        lang = self.get_user_lang(context)
        await update.message.reply_text(
            self.loc.get_text(lang, "select_language"),
            reply_markup=self.create_language_keyboard()
        )

    async def new_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create new QR"""
        await self.create_qr(update, context)

    async def cancel_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current operation"""
        lang = self.get_user_lang(context)
        context.user_data.pop('current_data_type', None)
        context.user_data.pop('wifi_data', None)
        context.user_data.pop('multi_step_data', None)

        await update.message.reply_text(
            self.loc.get_text(lang, "operation_cancelled"),
            reply_markup=self.create_main_menu_keyboard(lang)
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel conversation"""
        context.user_data.clear()
        await update.message.reply_text(
            "Operation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        await self.start(update, context)

    def run(self):
        """Start the bot"""
        print("🤖 QRGeneratorBot is running...")
        print(f"Available languages: {list(self.loc.get_available_languages().values())}")
        print("Press Ctrl+C to stop")
        self.application.run_polling()


if __name__ == '__main__':
    bot = QRBot()
    bot.run()