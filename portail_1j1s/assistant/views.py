import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .services.albert import AlbertAPIError, AlbertClient
from .services.markdown import render_assistant_markdown

CONVERSATION_SESSION_KEY = "assistant_1j1s_conversation"
CONVERSATION_EXPIRY_KEY = "assistant_1j1s_conversation_expiry"

CONVERSATION_LIFETIME_SECONDS = 30 * 60
CONVERSATION_MAX_MESSAGES = 20


def get_conversation_history(request):
    """Récupère l'historique non expiré de la conversation."""

    expiry = request.session.get(CONVERSATION_EXPIRY_KEY)
    now = timezone.now().timestamp()

    if not isinstance(expiry, (int, float)) or now >= expiry:
        request.session.pop(CONVERSATION_SESSION_KEY, None)
        request.session.pop(CONVERSATION_EXPIRY_KEY, None)
        return []

    history = request.session.get(CONVERSATION_SESSION_KEY, [])

    if not isinstance(history, list):
        return []

    return [
        entry
        for entry in history[-CONVERSATION_MAX_MESSAGES:]
        if (
            isinstance(entry, dict)
            and entry.get("role") in ("user", "assistant")
            and isinstance(entry.get("content"), str)
        )
    ]


def save_conversation_history(request, history):
    """Enregistre un historique limité et renouvelle son expiration."""

    request.session[CONVERSATION_SESSION_KEY] = history[
        -CONVERSATION_MAX_MESSAGES:
    ]

    request.session[CONVERSATION_EXPIRY_KEY] = (
        timezone.now().timestamp() + CONVERSATION_LIFETIME_SECONDS
    )


@require_POST
def assistant_chat(request):
    """Reçoit une question et retourne la réponse d'Albert API."""

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Le message envoyé est invalide."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Le message envoyé est invalide."},
            status=400,
        )

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return JsonResponse(
            {"error": "Merci de saisir une question."},
            status=400,
        )

    message = message.strip()

    if len(message) > 2000:
        return JsonResponse(
            {"error": "La question ne doit pas dépasser 2 000 caractères."},
            status=400,
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es l'assistant du portail public 1jeune1solution. "
                "Tu aides les jeunes à comprendre les démarches liées "
                "à l'orientation, à la formation, à l'emploi et aux aides. "
                "Réponds en français, clairement et sans inventer "
                "d'informations. Si tu ne sais pas, indique-le. "
                "Privilégie des réponses concises, avec des titres courts "
                "et des listes à puces lorsque cela facilite la lecture. "
                "N'utilise pas de tableaux Markdown : l'assistant est "
                "principalement consulté dans un panneau étroit sur mobile."
            ),
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    try:
        answer = AlbertClient().chat(messages)
    except AlbertAPIError:
        return JsonResponse(
            {
                "error": (
                    "L'assistant est momentanément indisponible. "
                    "Merci de réessayer."
                )
            },
            status=503,
        )

    return JsonResponse(
        {
            "answer": answer,
            "answer_html": render_assistant_markdown(answer),
        }
    )
