import tkinter as tk
from tkinter import scrolledtext
import re
import sys

# ----------- Core Chatbot Logic -----------

try:
    from langdetect import detect as ld_detect
except Exception:
    ld_detect = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

_KEYWORDS = {
    'greeting': {
        'en': ['hello', 'hi', 'hey'],
        'es': ['hola'],
        'fr': ['bonjour', 'salut'],
        'de': ['hallo'],
        'zh': ['你好', '您好'],
    },
    'order_status': {
        'en': ['order', 'status', 'tracking'],
        'es': ['pedido', 'estado', 'seguimiento'],
        'fr': ['commande', 'statut', 'suivi'],
        'de': ['bestellung', 'status', 'verfol'],
        'zh': ['订单', '状态', '跟踪'],
    },
    'refund': {
        'en': ['refund', 'return'],
        'es': ['reembolso', 'devolver'],
        'fr': ['remboursement', 'retour'],
        'de': ['rückerstattung', 'zurückgeben'],
        'zh': ['退款', '退货'],
    },
    'hours': {
        'en': ['hours', 'open', 'close', 'opening'],
        'es': ['horario', 'abre', 'cerrado'],
        'fr': ['horaire', 'ouvert', 'fermé'],
        'de': ['öffnungs', 'stunden', 'geschlossen'],
        'zh': ['营业', '时间', '几点'],
    },
}

_TEMPLATES = {
    'en': {
        'greeting': "Hello! How can I assist you today?",
        'order_status': "You can check your order status at: https://example.com/track. Do you want me to lookup an order number?",
        'refund': "I'm sorry to hear that. Please provide your order number and reason; I'll guide you through the refund process.",
        'hours': "Our support is available 9:00–17:00 (Mon–Fri). Would you like local times?",
        'fallback': "I didn't understand that. Can you rephrase or request a human agent?",
    },
    'es': {
        'greeting': "¡Hola! ¿En qué puedo ayudarte hoy?",
        'order_status': "Puedes revisar el estado de tu pedido en: https://example.com/track. ¿Quieres que busque un número de pedido?",
        'refund': "Lamento eso. Proporciona tu número de pedido y motivo; te guiaré en el reembolso.",
        'hours': "Nuestro soporte está disponible 9:00–17:00 (Lun–Vie). ¿Quieres horarios locales?",
        'fallback': "No entendí eso. ¿Puedes reformular o pedir un agente humano?",
    },
    'fr': {
        'greeting': "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        'order_status': "Vous pouvez vérifier le statut de votre commande : https://example.com/track. Voulez-vous que je recherche un numéro de commande ?",
        'refund': "Désolé d'entendre cela. Fournissez votre numéro de commande et la raison ; je vous guiderai pour le remboursement.",
        'hours': "Notre support est disponible de 9h00 à 17h00 (Lun–Ven). Voulez-vous les heures locales ?",
        'fallback': "Je n'ai pas compris. Pouvez-vous reformuler ou demander un agent humain ?",
    },
    'de': {
        'greeting': "Hallo! Wie kann ich Ihnen heute helfen?",
        'order_status': "Sie können den Bestellstatus prüfen: https://example.com/track. Soll ich nach einer Bestellnummer suchen?",
        'refund': "Das tut mir leid. Bitte geben Sie Ihre Bestellnummer und den Grund an; ich helfe beim Rückerstattungsprozess.",
        'hours': "Unser Support ist 9:00–17:00 (Mo–Fr) erreichbar. Möchten Sie lokale Zeiten?",
        'fallback': "Ich habe das nicht verstanden. Können Sie es umformulieren oder einen menschlichen Agenten anfordern?",
    },
    'zh': {
        'greeting': "您好！我能为您做些什么？",
        'order_status': "您可以在此检查订单状态：https://example.com/track。要我查询订单号吗？",
        'refund': "很抱歉。请提供订单号和原因，我将指导您退款流程。",
        'hours': "我们的支持时间为周一至周五9:00–17:00。您需要本地时间吗？",
        'fallback': "我不太明白。可以换一种说法或请求人工客服吗？",
    },
}


def escape_ssml(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


class CustomerSupportChatbot:
    def __init__(self, default_lang='en', tts=False):
        self.default_lang = default_lang if default_lang in _TEMPLATES else 'en'
        self.tts_enabled = tts and (pyttsx3 is not None)
        if self.tts_enabled:
            self._engine = pyttsx3.init()

    def detect_language(self, text):
        if not text or not text.strip():
            return self.default_lang
        if ld_detect:
            try:
                code = ld_detect(text)
                if code.startswith('zh'):
                    return 'zh'
                if code.startswith('en'):
                    return 'en'
                if code.startswith('es'):
                    return 'es'
                if code.startswith('fr'):
                    return 'fr'
                if code.startswith('de'):
                    return 'de'
                return self.default_lang
            except Exception:
                pass
        lower = text.lower()
        for lang in ('es', 'fr', 'de', 'zh'):
            for kws in _KEYWORDS.values():
                if lang in kws:
                    for kw in kws[lang]:
                        if kw.lower() in lower:
                            return lang
        return 'en'

    def _match_intent(self, text, lang):
        if not text:
            return 'fallback'
        search = text.lower()
        for intent, langs in _KEYWORDS.items():
            for kw in langs.get(lang, []):
                if kw.lower() in search:
                    return intent
        for intent, langs in _KEYWORDS.items():
            for kw in langs.get('en', []):
                if kw.lower() in search:
                    return intent
        return 'fallback'

    def generate_response(self, user_text, user_lang=None, include_extras=False):
        lang = user_lang or self.detect_language(user_text)
        if lang not in _TEMPLATES:
            lang = self.default_lang
        intent = self._match_intent(user_text, lang)
        template = _TEMPLATES.get(lang, {}).get(intent) or _TEMPLATES[self.default_lang]['fallback']
        resp = {
            'language': lang,
            'intent': intent,
            'text': template,
        }
        if include_extras:
            resp['confidence'] = 0.6 if intent == 'fallback' else 0.95
            resp['source'] = 'rule-based'
        return resp

    def accessible_output(self, response, screen_reader=False, aria_role='status'):
        text = response.get('text', '')
        payload = {
            'text': text,
            'aria': {
                'role': aria_role,
                'lang': response.get('language', self.default_lang),
            }
        }
        if screen_reader:
            ssml = f"<speak xml:lang=\"{payload['aria']['lang']}\">{escape_ssml(text)}</speak>"
            payload['ssml'] = ssml
        return payload


# ----------- GUI Section -----------

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Customer Support Chatbot")
        self.root.geometry("600x500")
        self.root.config(bg="#f3f4f6")

        self.bot = CustomerSupportChatbot(tts=False)

        tk.Label(
            root,
            text="Customer Support Chatbot",
            font=("Helvetica", 14, "bold"),
            bg="#2563eb",
            fg="white",
            pady=10
        ).pack(fill="x")

        self.chat_display = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state='disabled',
            font=("Arial", 11),
            bg="#ffffff",
            fg="#111827"
        )
        self.chat_display.pack(padx=10, pady=10, fill="both", expand=True)

        input_frame = tk.Frame(root, bg="#f3f4f6")
        input_frame.pack(fill="x", padx=10, pady=5)

        self.user_input = tk.Entry(input_frame, font=("Arial", 12))
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="white",
            padx=15,
            relief="flat",
            cursor="hand2"
        )
        self.send_button.pack(side="right")

        self.user_input.bind("<Return>", lambda event: self.send_message())

        self._insert_bot_message("Hello! I'm your support assistant. How can I help you today?")

    def _insert_user_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"\n👤 You: {message}\n", "user")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def _insert_bot_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"🤖 Bot: {message}\n", "bot")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def send_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self._insert_user_message(user_text)
        self.user_input.delete(0, tk.END)

        response = self.bot.generate_response(user_text)
        payload = self.bot.accessible_output(response, screen_reader=True)
        bot_reply = payload['text']
        self._insert_bot_message(bot_reply)


# ----------- Run GUI -----------
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()
