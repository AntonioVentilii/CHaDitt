localized_messages = {
    "en": {
        "unsupported_content": "Sorry, my only purpose is to process audio messages. "
                               "I can't process {message_type} yet.",
        "changed_language": "Your language has been changed to \'{language}\'.",
        "language_not_supported": "Sorry, I can't process messages in \'{language}\' yet.",
        "header": "TRANSCRIPTION",
        "context_not_found": "It seems I forgot already about that message. Please send it again.",
        "correction_header": "CORRECTION",
        "summary_header": "SUMMARY",
        "translation_header": "TRANSLATION",
        "btn_correct": "✍️ Correct",
        "btn_summary": "📝 Summarize",
        "btn_translate": "🌍 Translate",
        "actions_prompt": "What should I do with this transcription?",
        "translate_prompt": "Which language should I translate it into?",
        "translate_button": "Choose language",
        "translate_section": "Languages",
        "action_failed": "Sorry, something went wrong. Please try again in a moment.",
    },
    "it": {
        "unsupported_content": "Mi dispiace, il mio unico scopo è elaborare messaggi audio. "
                               "Non posso ancora elaborare {message_type}.",
        "changed_language": "La tua lingua è stata cambiata in \'{language}\'.",
        "language_not_supported": "Mi dispiace, non posso ancora elaborare messaggi in \'{language}\'.",
        "header": "TRASCRIZIONE",
        "context_not_found": "Sembra che abbia già dimenticato quel messaggio. Per favore invialo di nuovo.",
        "correction_header": "CORREZIONE",
        "summary_header": "RIASSUNTO",
        "translation_header": "TRADUZIONE",
        "btn_correct": "✍️ Correggi",
        "btn_summary": "📝 Riassumi",
        "btn_translate": "🌍 Traduci",
        "actions_prompt": "Cosa vuoi che faccia con questa trascrizione?",
        "translate_prompt": "In che lingua vuoi che la traduca?",
        "translate_button": "Scegli la lingua",
        "translate_section": "Lingue",
        "action_failed": "Mi dispiace, qualcosa è andato storto. Riprova tra un attimo.",
    },
    "es": {
        "unsupported_content": "Lo siento, mi único propósito es procesar mensajes de audio. "
                               "No puedo procesar {message_type} aún.",
        "changed_language": "Tu idioma ha sido cambiado a \'{language}\'.",
        "language_not_supported": "Lo siento, no puedo procesar mensajes en \'{language}\' aún.",
        "header": "TRANSCRIPCIÓN",
        "context_not_found": "Parece que ya olvidé ese mensaje. Por favor envíalo de nuevo.",
        "correction_header": "CORRECCIÓN",
        "summary_header": "RESUMEN",
        "translation_header": "TRADUCCIÓN",
        "btn_correct": "✍️ Corregir",
        "btn_summary": "📝 Resumir",
        "btn_translate": "🌍 Traducir",
        "actions_prompt": "¿Qué hago con esta transcripción?",
        "translate_prompt": "¿A qué idioma la traduzco?",
        "translate_button": "Elegir idioma",
        "translate_section": "Idiomas",
        "action_failed": "Lo siento, algo salió mal. Inténtalo de nuevo en un momento.",
    },
    "pt": {
        "unsupported_content": "Desculpe, meu único propósito é processar mensagens de áudio. "
                               "Não consigo processar {message_type} ainda.",
        "changed_language": "Seu idioma foi alterado para \'{language}\'.",
        "language_not_supported": "Desculpe, ainda não consigo processar mensagens em \'{language}\'.",
        "header": "TRANSCRIÇÃO",
        "context_not_found": "Parece que já esqueci daquela mensagem. Por favor, envie-a novamente.",
        "correction_header": "CORREÇÃO",
        "summary_header": "RESUMO",
        "translation_header": "TRADUÇÃO",
        "btn_correct": "✍️ Corrigir",
        "btn_summary": "📝 Resumir",
        "btn_translate": "🌍 Traduzir",
        "actions_prompt": "O que devo fazer com esta transcrição?",
        "translate_prompt": "Para qual idioma devo traduzir?",
        "translate_button": "Escolher idioma",
        "translate_section": "Idiomas",
        "action_failed": "Desculpe, algo deu errado. Tente novamente daqui a pouco.",
    },
    "fr": {
        "unsupported_content": "Désolé, mon seul but est de traiter les messages audio. "
                               "Je ne peux pas traiter {message_type} encore.",
        "changed_language": "Votre langue a été changée en \'{language}\'.",
        "language_not_supported": "Désolé, je ne peux pas encore traiter les messages en \'{language}\'.",
        "header": "TRANSCRIPTION",
        "context_not_found": "Il semble que j'ai déjà oublié ce message. Veuillez le renvoyer.",
        "correction_header": "CORRECTION",
        "summary_header": "RÉSUMÉ",
        "translation_header": "TRADUCTION",
        "btn_correct": "✍️ Corriger",
        "btn_summary": "📝 Résumer",
        "btn_translate": "🌍 Traduire",
        "actions_prompt": "Que dois-je faire de cette transcription ?",
        "translate_prompt": "Dans quelle langue dois-je la traduire ?",
        "translate_button": "Choisir la langue",
        "translate_section": "Langues",
        "action_failed": "Désolé, quelque chose s'est mal passé. Réessayez dans un instant.",
    },
    "de": {
        "unsupported_content": "Entschuldigung, mein einziger Zweck ist es, Sprachnachrichten zu verarbeiten. "
                               "Ich kann {message_type} noch nicht verarbeiten.",
        "changed_language": "Ihre Sprache wurde auf \'{language}\' geändert.",
        "language_not_supported": "Entschuldigung, ich kann Nachrichten in \'{language}\' noch nicht verarbeiten.",
        "header": "TRANSCRIPTION",
        "context_not_found": "Es scheint, als hätte ich diese Nachricht bereits vergessen. Bitte senden Sie sie erneut.",
        "correction_header": "KORREKTUR",
        "summary_header": "ZUSAMMENFASSUNG",
        "translation_header": "ÜBERSETZUNG",
        "btn_correct": "✍️ Korrigieren",
        "btn_summary": "📝 Zusammenfassen",
        "btn_translate": "🌍 Übersetzen",
        "actions_prompt": "Was soll ich mit dieser Transkription machen?",
        "translate_prompt": "In welche Sprache soll ich sie übersetzen?",
        "translate_button": "Sprache wählen",
        "translate_section": "Sprachen",
        "action_failed": "Entschuldigung, etwas ist schiefgelaufen. Bitte versuchen Sie es gleich noch einmal.",
    },
}

DEFAULT_LANGUAGE = 'it'

AVAILABLE_LANGUAGES = list(localized_messages.keys())

# How each language calls itself (shown in the translation menu) and its English name (given to the model).
LANGUAGE_NAMES = {
    "it": ("🇮🇹 Italiano", "Italian"),
    "en": ("🇬🇧 English", "English"),
    "es": ("🇪🇸 Español", "Spanish"),
    "pt": ("🇵🇹 Português", "Portuguese"),
    "fr": ("🇫🇷 Français", "French"),
    "de": ("🇩🇪 Deutsch", "German"),
}


def get_localized_message(language_iso: str, message_key: str, **kwargs) -> str:
    language_messages = localized_messages.get(language_iso, localized_messages[DEFAULT_LANGUAGE])
    if message_key not in language_messages:
        raise ValueError(f"Message key \'{message_key}\' not found in localized messages for "
                         f"language \'{language_iso}\'")
    return language_messages[message_key].format(**kwargs)


def check_supported_language(iso_code: str, language: str) -> tuple[bool, str]:
    if iso_code in localized_messages:
        ret = get_localized_message(iso_code, 'changed_language', language=iso_code)
        success = True
    else:
        ret = get_localized_message(language, 'language_not_supported', language=iso_code)
        success = False
    return success, ret
