import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services.albert import AlbertAPIError, AlbertClient


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
                "d'informations. Si tu ne sais pas, indique-le."
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

    return JsonResponse({"answer": answer})
