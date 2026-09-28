from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .emails import notify_new_application, notify_new_contact_message
from .forms import ApplicationForm, ContactForm
from .models import (
    SiteSettings, HeroSection, AboutSection, AcademicsSection, AdmissionsSection, OpeningsSection,
    ResearchSection, ResearchAreasSection, CampusSection, GallerySection, ApplySection, ContactSection,
    CtaSection,
)


def home(request, apply_form=None, contact_form=None):
    hero = HeroSection.load()
    about = AboutSection.load()
    academics = AcademicsSection.load()
    admissions = AdmissionsSection.load()
    openings = OpeningsSection.load()
    research = ResearchSection.load()
    research_areas = ResearchAreasSection.load()
    campus = CampusSection.load()
    gallery = GallerySection.load()
    gallery_images = gallery.images.filter(is_active=True).select_related('category')
    apply = ApplySection.load()
    contact = ContactSection.load()
    cta = CtaSection.load()

    context = {
        'hero': hero if hero.is_active else None,
        'hero_tag_words': hero.tag_words.filter(is_active=True),

        'about': about if about.is_active else None,
        'about_features': about.features.filter(is_active=True),

        'academics': academics if academics.is_active else None,
        'programs': academics.programs.filter(is_active=True),

        'admissions': admissions if admissions.is_active else None,

        'openings': openings if openings.is_active else None,
        'course_openings': openings.courses.filter(is_active=True).select_related('section'),

        'research': research if research.is_active else None,

        'research_areas': research_areas if research_areas.is_active else None,
        'research_tags': research_areas.tags.filter(is_active=True),
        'research_focus_items': research_areas.focus_items.filter(is_active=True),

        'campus': campus if campus.is_active else None,
        'campus_facilities': campus.facilities.filter(is_active=True),

        'gallery': gallery if gallery.is_active else None,
        'gallery_images': gallery_images,
        # only categories that have at least one visible photo get a filter button
        'gallery_categories': gallery.categories.filter(
            is_active=True, images__in=gallery_images).distinct(),

        'apply': apply if apply.is_active else None,
        'apply_points': apply.points.filter(is_active=True),
        'apply_form': apply_form or ApplicationForm(section=apply, auto_id='apply_%s'),

        'contact': contact if contact.is_active else None,
        'contact_form': contact_form or ContactForm(section=contact, auto_id='contact_%s'),

        'cta': cta if cta.is_active else None,
    }
    return render(request, 'index.html', context)


# =====================================================================
# Form submissions
# =====================================================================

def _wants_json(request):
    return (request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('accept', ''))


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')


def _handle_form(request, form, section, anchor, notify, form_kwarg):
    """
    Shared submit flow for both forms.
    - JavaScript (fetch/AJAX) requests get JSON: {ok, message} or {ok: false, errors}.
    - Normal form posts redirect back to the section with a message,
      or re-render the page with the errors shown.
    """
    if form.is_valid():
        obj = form.save(commit=False)
        obj.ip_address = _client_ip(request)
        obj.save()
        notify(obj, section, SiteSettings.load())

        if _wants_json(request):
            return JsonResponse({'ok': True, 'message': section.success_message})
        messages.success(request, section.success_message, extra_tags=anchor)
        return redirect(f'/#{anchor}')

    if _wants_json(request):
        errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
        return JsonResponse({'ok': False, 'errors': errors}, status=400)
    return home(request, **{form_kwarg: form})


@require_POST
def submit_application(request):
    section = ApplySection.load()
    form = ApplicationForm(request.POST, section=section, auto_id='apply_%s')
    return _handle_form(request, form, section, 'apply', notify_new_application, 'apply_form')


@require_POST
def submit_contact(request):
    section = ContactSection.load()
    form = ContactForm(request.POST, section=section, auto_id='contact_%s')
    return _handle_form(request, form, section, 'contact', notify_new_contact_message, 'contact_form')
