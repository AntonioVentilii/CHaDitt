localized_messages = {
    "en": {
        "audio_processing": "I'm converting your audio message to text. Please wait...",
        "unsupported_content": "Sorry, my only purpose is to process audio messages. "
                               "I can't process {message_type} yet.",
        "changed_language": "Your language has been changed to \'{language}\'.",
        "language_not_supported": "Sorry, I can't process messages in \'{language}\' yet.",
        "header": "TRANSCRIPTION",
        "footer": """Answer this message with:
1 - Try and correct the grammar.
2 - Summary.
3 - Translation.
""",
        "choice_not_recognized": "Choice not recognized. Please choose between:",
        "context_not_found": "It seems I forgot already about that message. Please send it again.",
        "correction_header": "CORRECTION",
        "summary_header": "SUMMARY",
        "translation_header": "TRANSLATION",
    },
    "it": {
        "audio_processing": "Sto trasformando il tuo messaggio audio in testo. Attendere prego...",
        "unsupported_content": "Mi dispiace, il mio unico scopo è elaborare messaggi audio. "
                               "Non posso ancora elaborare {message_type}.",
        "changed_language": "La tua lingua è stata cambiata in \'{language}\'.",
        "language_not_supported": "Mi dispiace, non posso ancora elaborare messaggi in \'{language}\'.",
        "header": "TRASCRIZIONE",
        "footer": """Rispondi a questo messaggio con:
1 - Prova a correggere la grammatica.
2 - Riassunto.
3 - Traduzione.
""",
        "choice_not_recognized": "Scelta non riconosciuta. Scegli tra:",
        "context_not_found": "Sembra che abbia già dimenticato quel messaggio. Per favore invialo di nuovo.",
        "correction_header": "CORREZIONE",
        "summary_header": "RIASSUNTO",
        "translation_header": "TRADUZIONE",
    },
    "es": {
        "audio_processing": "Estoy convirtiendo tu mensaje de audio a texto. Por favor espera...",
        "unsupported_content": "Lo siento, mi único propósito es procesar mensajes de audio. "
                               "No puedo procesar {message_type} aún.",
        "changed_language": "Tu idioma ha sido cambiado a \'{language}\'.",
        "language_not_supported": "Lo siento, no puedo procesar mensajes en \'{language}\' aún.",
        "header": "TRANSCRIPCIÓN",
        "footer": """Responde a este mensaje con:
1 - Intentar corregir la gramática.
2 - Resumen.
3 - Traducción.
""",
        "choice_not_recognized": "Opción no reconocida. Por favor elige entre:",
        "context_not_found": "Parece que ya olvidé ese mensaje. Por favor envíalo de nuevo.",
        "correction_header": "CORRECCIÓN",
        "summary_header": "RESUMEN",
        "translation_header": "TRADUCCIÓN",
    },
    "pt": {
        "audio_processing": "Estou convertendo sua mensagem de áudio em texto. Por favor, aguarde...",
        "unsupported_content": "Desculpe, meu único propósito é processar mensagens de áudio. "
                               "Não consigo processar {message_type} ainda.",
        "changed_language": "Seu idioma foi alterado para \'{language}\'.",
        "language_not_supported": "Desculpe, ainda não consigo processar mensagens em \'{language}\'.",
        "header": "TRANSCRIÇÃO",
        "footer": """Responda a esta mensagem com:
1 - Tentar corrigir a gramática.
2 - Resumo.
3 - Tradução.
""",
        "choice_not_recognized": "Escolha não reconhecida. Por favor, escolha entre:",
        "context_not_found": "Parece que já esqueci daquela mensagem. Por favor, envie-a novamente.",
        "correction_header": "CORREÇÃO",
        "summary_header": "RESUMO",
        "translation_header": "TRADUÇÃO",
    },
    "fr": {
        "audio_processing": "Je convertis votre message audio en texte. Veuillez patienter...",
        "unsupported_content": "Désolé, mon seul but est de traiter les messages audio. "
                               "Je ne peux pas traiter {message_type} encore.",
        "changed_language": "Votre langue a été changée en \'{language}\'.",
        "language_not_supported": "Désolé, je ne peux pas encore traiter les messages en \'{language}\'.",
        "header": "TRANSCRIPTION",
        "footer": """Répondez à ce message avec:
1 - Essayer de corriger la grammaire.
2 - Résumé.
3 - Traduction.
""",
        "choice_not_recognized": "Choix non reconnu. Veuillez choisir entre:",
        "context_not_found": "Il semble que j'ai déjà oublié ce message. Veuillez le renvoyer.",
        "correction_header": "CORRECTION",
        "summary_header": "RÉSUMÉ",
        "translation_header": "TRADUCTION",
    },
    "de": {
        "audio_processing": "Ich konvertiere Ihre Sprachnachricht in Text. Bitte warten...",
        "unsupported_content": "Entschuldigung, mein einziger Zweck ist es, Sprachnachrichten zu verarbeiten. "
                               "Ich kann {message_type} noch nicht verarbeiten.",
        "changed_language": "Ihre Sprache wurde auf \'{language}\' geändert.",
        "language_not_supported": "Entschuldigung, ich kann Nachrichten in \'{language}\' noch nicht verarbeiten.",
        "header": "TRANSCRIPTION",
        "footer": """Beantworten Sie diese Nachricht mit:
1 - Versuchen Sie, die Grammatik zu korrigieren.
2 - Zusammenfassung.
3 - Übersetzung.
""",
        "choice_not_recognized": "Auswahl nicht erkannt. Bitte wählen Sie zwischen:",
        "context_not_found": "Es scheint, als hätte ich diese Nachricht bereits vergessen. Bitte senden Sie sie erneut.",
        "correction_header": "KORREKTUR",
        "summary_header": "ZUSAMMENFASSUNG",
        "translation_header": "ÜBERSETZUNG",
    },
}

DEFAULT_LANGUAGE = 'it'

AVAILABLE_LANGUAGES = list(localized_messages.keys())


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
