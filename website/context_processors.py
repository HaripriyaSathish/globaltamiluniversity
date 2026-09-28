from .models import SiteSettings, Navbar, FloatingButton, Footer, QuickLink, ProgramLink, LegalLink


def site_settings(request):
    """Global data used on every page: SEO, branding, topbar, navbar, floating buttons, footer."""
    site = SiteSettings.load()
    navbar = Navbar.load()
    footer = Footer.load()

    floating_buttons = []
    for btn in FloatingButton.objects.filter(is_active=True):
        btn.href = btn.get_href(site)
        if btn.href:
            floating_buttons.append(btn)

    return {
        'site': site,
        'navbar': navbar,
        'nav_items': navbar.items.filter(is_active=True),
        'floating_buttons': floating_buttons,

        'footer': footer,
        'footer_logo': footer.logo or site.logo,
        'footer_name': footer.name or site.university_name,
        'footer_quick_links': QuickLink.objects.filter(footer=footer, is_active=True),
        'footer_program_links': ProgramLink.objects.filter(footer=footer, is_active=True),
        'footer_legal_links': LegalLink.objects.filter(footer=footer, is_active=True),
        # shown even before a URL is added (icon without link until then)
        'footer_social_links': footer.social_links.filter(is_active=True),
    }
