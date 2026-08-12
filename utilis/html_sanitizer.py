import bleach

ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4",
    "ul", "ol", "li",
    "strong", "em",
    "blockquote",
    "a",
    "img",
    "br",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href"],
    "img": ["src", "alt"],
}

def sanitize_html(content: str):
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )