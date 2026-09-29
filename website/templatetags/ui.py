"""
Template helpers for the frontend.

    {% load ui %}
    {% icon 'mail' %}                    -> inline SVG (outline style, like the design)
    {% icon 'mail' size=16 class='x' %}
"""
from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()

# Outline icons (24×24 viewBox, stroke = currentColor) matching the Figma design.
ICONS = {
    'map-pin': '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/>'
               '<circle cx="12" cy="10" r="3"/>',
    'mail': '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67'
             'A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6'
             'l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    'phone-outgoing': '<polyline points="22 8 22 2 16 2"/><line x1="16" x2="22" y1="8" y2="2"/>'
                      '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 '
                      '19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 '
                      '2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 '
                      '2.81.7A2 2 0 0 1 22 16.92z"/>',
    'whatsapp': '<path d="M3.5 20.5l1.3-4.1A8.6 8.6 0 1 1 8 19.4z"/>'
                '<path d="M9.2 8.3c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.6 1.5c.1.2 0 .5-.1.6l-.5.6c-.1.2-.1.4 0 .5'
                '.6 1 1.4 1.8 2.4 2.4.2.1.4.1.5 0l.6-.5c.2-.1.4-.2.6-.1l1.5.6c.3.1.4.3.4.5v.5c0 .3 0 .5-.4.7'
                '-.5.3-1.2.5-1.9.4-2.6-.4-5.2-3-5.6-5.6-.1-.7.1-1.4.4-1.9z"/>',
    'arrow-right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    'chevron-down': '<path d="m6 9 6 6 6-6"/>',

    # Academic program icons (outline, as in the design)
    'graduation-cap': '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832'
                      'l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    'book-open': '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    'library': '<path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/>',
    'briefcase': '<path d="M12 12h.01"/><path d="M16 6V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'
                 '<path d="M22 13a18.15 18.15 0 0 1-20 0"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
    'school': '<path d="M14 22v-4a2 2 0 1 0-4 0v4"/><path d="m18 10 3.447 1.724a1 1 0 0 1 .553.894V20a2 2 0 0 1-2 2H4'
              'a2 2 0 0 1-2-2v-7.382a1 1 0 0 1 .553-.894L6 10"/><path d="M18 5v17"/>'
              '<path d="m4 6 7.106-3.553a2 2 0 0 1 1.788 0L20 6"/><path d="M6 5v17"/><circle cx="12" cy="9" r="2"/>',
    'microscope': '<path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2"/>'
                  '<path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/>',
    'menu': '<line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="12" y2="12"/>'
            '<line x1="4" x2="20" y1="18" y2="18"/>',
    'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
}


@register.filter
def break_last_word(value):
    """'GLOBAL TAMIL UNIVERSITY' -> 'GLOBAL TAMIL<br>UNIVERSITY' (last word on its own line)."""
    words = str(value or '').split()
    if len(words) < 2:
        return value
    return format_html('{}<br>{}', ' '.join(words[:-1]), words[-1])


@register.simple_tag
def any_icon(value, size=24, stroke=1.6):
    """
    Icon chosen in admin: a built-in outline icon name (e.g. "graduation-cap")
    or a Font Awesome class (e.g. "fa-solid fa-flask").
    """
    value = (value or '').strip()
    if value in ICONS:
        return icon(value, size=size, stroke=stroke)
    if value:
        return format_html('<i class="{}" aria-hidden="true"></i>', value)
    return ''


@register.simple_tag
def icon(name, size=24, stroke=2, cls=''):
    body = ICONS.get(name)
    if not body:
        return ''
    return format_html(
        '<svg class="icon icon-{} {}" width="{}" height="{}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="{}" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">{}</svg>',
        name, cls, size, size, stroke, mark_safe(body),
    )
