localized_messages = {
    "en": {
        "language_name": "English",
        "unsupported_content": "Sorry, my only purpose is to process audio messages. "
                               "I can't process {message_type} yet.",
        "changed_language": "Your language has been changed to \'{language}\'.",
        "language_not_supported": "Sorry, I can't process messages in \'{language}\' yet.",
        "header": "TRANSCRIPTION",
        "actions_prompt": "What should I do with this transcription?",
        "correct_button": "Correct",
        "summarize_button": "Summarize",
        "translate_button": "Translate",
        "correct_header": "CORRECTION",
        "summarize_header": "SUMMARY",
        "translate_header": "TRANSLATION",
        "choice_not_recognized": "Choice not recognized. Tap one of the buttons under the transcription.",
        "context_not_found": "It seems I forgot already about that message. Please send it again.",
        "action_failed": "Sorry, something went wrong. Please try again in a moment.",
    },
    "it": {
        "language_name": "Italian",
        "unsupported_content": "Mi dispiace, il mio unico scopo è elaborare messaggi audio. "
                               "Non posso ancora elaborare {message_type}.",
        "changed_language": "La tua lingua è stata cambiata in \'{language}\'.",
        "language_not_supported": "Mi dispiace, non posso ancora elaborare messaggi in \'{language}\'.",
        "header": "TRASCRIZIONE",
        "actions_prompt": "Cosa faccio con questa trascrizione?",
        "correct_button": "Correggi",
        "summarize_button": "Riassumi",
        "translate_button": "Traduci",
        "correct_header": "CORREZIONE",
        "summarize_header": "RIASSUNTO",
        "translate_header": "TRADUZIONE",
        "choice_not_recognized": "Scelta non riconosciuta. Tocca uno dei bottoni sotto la trascrizione.",
        "context_not_found": "Sembra che abbia già dimenticato quel messaggio. Per favore invialo di nuovo.",
        "action_failed": "Mi dispiace, qualcosa è andato storto. Riprova tra poco.",
    },
    "es": {
        "language_name": "Spanish",
        "unsupported_content": "Lo siento, mi único propósito es procesar mensajes de audio. "
                               "No puedo procesar {message_type} aún.",
        "changed_language": "Tu idioma ha sido cambiado a \'{language}\'.",
        "language_not_supported": "Lo siento, no puedo procesar mensajes en \'{language}\' aún.",
        "header": "TRANSCRIPCIÓN",
        "actions_prompt": "¿Qué hago con esta transcripción?",
        "correct_button": "Corregir",
        "summarize_button": "Resumir",
        "translate_button": "Traducir",
        "correct_header": "CORRECCIÓN",
        "summarize_header": "RESUMEN",
        "translate_header": "TRADUCCIÓN",
        "choice_not_recognized": "Opción no reconocida. Toca uno de los botones debajo de la transcripción.",
        "context_not_found": "Parece que ya olvidé ese mensaje. Por favor envíalo de nuevo.",
        "action_failed": "Lo siento, algo salió mal. Inténtalo de nuevo en un momento.",
    },
    "pt": {
        "language_name": "Brazilian Portuguese",
        "unsupported_content": "Desculpe, meu único propósito é processar mensagens de áudio. "
                               "Não consigo processar {message_type} ainda.",
        "changed_language": "Seu idioma foi alterado para \'{language}\'.",
        "language_not_supported": "Desculpe, ainda não consigo processar mensagens em \'{language}\'.",
        "header": "TRANSCRIÇÃO",
        "actions_prompt": "O que faço com esta transcrição?",
        "correct_button": "Corrigir",
        "summarize_button": "Resumir",
        "translate_button": "Traduzir",
        "correct_header": "CORREÇÃO",
        "summarize_header": "RESUMO",
        "translate_header": "TRADUÇÃO",
        "choice_not_recognized": "Escolha não reconhecida. Toque em um dos botões abaixo da transcrição.",
        "context_not_found": "Parece que já esqueci daquela mensagem. Por favor, envie-a novamente.",
        "action_failed": "Desculpe, algo deu errado. Tente de novo daqui a pouco.",
    },
    "fr": {
        "language_name": "French",
        "unsupported_content": "Désolé, mon seul but est de traiter les messages audio. "
                               "Je ne peux pas traiter {message_type} encore.",
        "changed_language": "Votre langue a été changée en \'{language}\'.",
        "language_not_supported": "Désolé, je ne peux pas encore traiter les messages en \'{language}\'.",
        "header": "TRANSCRIPTION",
        "actions_prompt": "Que dois-je faire de cette transcription ?",
        "correct_button": "Corriger",
        "summarize_button": "Résumer",
        "translate_button": "Traduire",
        "correct_header": "CORRECTION",
        "summarize_header": "RÉSUMÉ",
        "translate_header": "TRADUCTION",
        "choice_not_recognized": "Choix non reconnu. Touchez l'un des boutons sous la transcription.",
        "context_not_found": "Il semble que j'ai déjà oublié ce message. Veuillez le renvoyer.",
        "action_failed": "Désolé, quelque chose s'est mal passé. Réessayez dans un instant.",
    },
    "de": {
        "language_name": "German",
        "unsupported_content": "Entschuldigung, mein einziger Zweck ist es, Sprachnachrichten zu verarbeiten. "
                               "Ich kann {message_type} noch nicht verarbeiten.",
        "changed_language": "Ihre Sprache wurde auf \'{language}\' geändert.",
        "language_not_supported": "Entschuldigung, ich kann Nachrichten in \'{language}\' noch nicht verarbeiten.",
        "header": "TRANSKRIPTION",
        "actions_prompt": "Was soll ich mit dieser Transkription machen?",
        "correct_button": "Korrigieren",
        "summarize_button": "Zusammenfassen",
        "translate_button": "Übersetzen",
        "correct_header": "KORREKTUR",
        "summarize_header": "ZUSAMMENFASSUNG",
        "translate_header": "ÜBERSETZUNG",
        "choice_not_recognized": "Auswahl nicht erkannt. Tippen Sie auf eine der Schaltflächen unter der "
                                 "Transkription.",
        "context_not_found": "Es scheint, als hätte ich diese Nachricht bereits vergessen. Bitte senden Sie sie "
                             "erneut.",
        "action_failed": "Entschuldigung, etwas ist schiefgelaufen. Bitte versuchen Sie es gleich noch einmal.",
    },
}

DEFAULT_LANGUAGE = 'it'

AVAILABLE_LANGUAGES = list(localized_messages.keys())

# A sender's language before they choose one, from the country calling code their WhatsApp id starts with: the
# countries where one supported language is the main one. Codes shared by several supported languages
# (Switzerland 41, Belgium 32, Luxembourg 352, Cameroon 237) are left out, so those senders get the default
# language until they write which one they want. The longest matching code wins, so +1 787 (Puerto Rico) is Spanish
# while the rest of +1 is English.
COUNTRY_CALLING_CODE_LANGUAGES = {
    # English
    '1': 'en', '44': 'en', '353': 'en', '61': 'en', '64': 'en', '27': 'en', '234': 'en', '233': 'en', '254': 'en',
    '256': 'en', '263': 'en', '260': 'en', '265': 'en', '267': 'en', '1876': 'en', '1868': 'en',
    # Italian
    '39': 'it', '378': 'it', '379': 'it',
    # Portuguese
    '55': 'pt', '351': 'pt', '244': 'pt', '258': 'pt', '238': 'pt', '245': 'pt', '239': 'pt', '670': 'pt',
    # Spanish
    '34': 'es', '52': 'es', '54': 'es', '56': 'es', '57': 'es', '58': 'es', '51': 'es', '53': 'es', '591': 'es',
    '593': 'es', '595': 'es', '598': 'es', '502': 'es', '503': 'es', '504': 'es', '505': 'es', '506': 'es',
    '507': 'es', '240': 'es', '1787': 'es', '1939': 'es', '1809': 'es', '1829': 'es', '1849': 'es',
    # French
    '33': 'fr', '377': 'fr', '221': 'fr', '223': 'fr', '224': 'fr', '225': 'fr', '226': 'fr', '227': 'fr',
    '228': 'fr', '229': 'fr', '241': 'fr', '242': 'fr', '243': 'fr', '261': 'fr', '509': 'fr', '262': 'fr',
    '590': 'fr', '594': 'fr', '596': 'fr', '687': 'fr', '689': 'fr',
    # German
    '49': 'de', '43': 'de', '423': 'de',
}
LONGEST_CALLING_CODE = max(len(code) for code in COUNTRY_CALLING_CODE_LANGUAGES)


def language_for_wa_id(wa_id: str) -> str:
    for length in range(LONGEST_CALLING_CODE, 0, -1):
        language = COUNTRY_CALLING_CODE_LANGUAGES.get(wa_id[:length])
        if language:
            return language
    return DEFAULT_LANGUAGE


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
