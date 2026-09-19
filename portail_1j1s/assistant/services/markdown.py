import bleach
import markdown


ALLOWED_TAGS = [
    "p", "br", "strong", "em", "del",
    "h2", "h3", "h4",
    "ul", "ol", "li",
    "blockquote", "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td",
    "a", "hr",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "th": ["align"],
    "td": ["align"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def render_assistant_markdown(content):
    """Convertit une réponse Markdown d'Albert en HTML assaini."""

    html = markdown.markdown(
        content,
        extensions=["extra", "sane_lists"],
    )

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
