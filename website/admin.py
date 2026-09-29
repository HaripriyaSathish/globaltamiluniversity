import csv

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    SiteSettings, Navbar, NavMenuItem, HeroSection, HeroTagWord, FloatingButton,
    AboutSection, AboutFeature, AcademicsSection, Program,
    AdmissionsSection, OpeningsSection, CourseOpening,
    ResearchSection, ResearchAreasSection, ResearchTag, ResearchFocus,
    CampusSection, CampusFacility, GallerySection, GalleryCategory, GalleryImage,
    ApplySection, ApplyPoint, Application, FaqSection, FaqItem, ContactSection, ContactSubject, ContactMessage,
    CtaSection, Footer, QuickLink, ProgramLink, LegalLink, SocialLink,
)


# =====================================================================
# Helpers
# =====================================================================

class BaseAdmin(admin.ModelAdmin):
    save_on_top = True      # Save buttons above and below the form


class SingletonAdmin(BaseAdmin):
    """Admin for one-row models: no add/delete, list page opens the edit form."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        opts = self.model._meta
        return redirect(reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[obj.pk]))


def make_image_preview(field_name, height=60):
    def _preview(self, obj):
        img = getattr(obj, field_name, None)
        if img:
            return format_html('<img src="{}" style="height:{}px;border-radius:4px;" />', img.url, height)
        return "—"
    _preview.short_description = "Preview"
    return _preview


# =====================================================================
# Site settings
# =====================================================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    readonly_fields = ('logo_preview', 'favicon_preview', 'og_image_preview', 'updated_at')
    fieldsets = (
        ("SEO", {'fields': ('meta_title', 'meta_description', 'meta_keywords',
                            'og_image', 'og_image_preview', 'favicon', 'favicon_preview')}),
        ("Branding", {'fields': ('logo', 'logo_preview', 'university_name', 'established_text')}),
        ("Contact details (Top bar, floating buttons, contact & footer)", {
            'fields': ('address', 'email', 'phone', 'whatsapp_number')}),
        ("Top bar", {'fields': ('show_topbar',)}),
        ("Info", {'fields': ('updated_at',)}),
    )

    logo_preview = make_image_preview('logo')
    favicon_preview = make_image_preview('favicon', 32)
    og_image_preview = make_image_preview('og_image', 80)


# =====================================================================
# Navbar
# =====================================================================

class NavMenuItemInline(admin.TabularInline):
    model = NavMenuItem
    extra = 0
    fields = ('order', 'label', 'link', 'open_in_new_tab', 'is_active')


@admin.register(Navbar)
class NavbarAdmin(SingletonAdmin):
    fields = ('cta_text', 'cta_link', 'is_sticky')
    inlines = [NavMenuItemInline]


# =====================================================================
# Hero
# =====================================================================

class HeroTagWordInline(admin.TabularInline):
    model = HeroTagWord
    extra = 0
    fields = ('order', 'text', 'is_active')


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    readonly_fields = ('background_preview',)
    fieldsets = (
        ("Heading", {'fields': ('title_line_1', 'title_highlight', 'subtitle', 'description')}),
        ("Button", {'fields': ('button_text', 'button_link')}),
        ("Background", {'fields': ('background_image', 'background_preview')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [HeroTagWordInline]

    background_preview = make_image_preview('background_image', 120)


# =====================================================================
# Floating buttons
# =====================================================================

@admin.register(FloatingButton)
class FloatingButtonAdmin(BaseAdmin):
    list_display = ('label', 'button_type', 'link', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('button_type', 'is_active')
    fields = ('button_type', 'label', 'link', 'open_in_new_tab', 'order', 'is_active')


# =====================================================================
# About
# =====================================================================

class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 0
    fields = ('order', 'title', 'icon_class', 'is_active')


@admin.register(AboutSection)
class AboutSectionAdmin(SingletonAdmin):
    readonly_fields = ('image_preview',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Image", {'fields': ('image', 'image_preview', 'image_alt')}),
        ("Link", {'fields': ('link_text', 'link_url')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [AboutFeatureInline]

    image_preview = make_image_preview('image', 120)


# =====================================================================
# Academics
# =====================================================================

class ProgramInline(admin.TabularInline):
    model = Program
    extra = 0
    fields = ('order', 'title', 'duration', 'subjects', 'icon_class', 'is_active')


@admin.register(AcademicsSection)
class AcademicsSectionAdmin(SingletonAdmin):
    readonly_fields = ('background_preview',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Button", {'fields': ('button_text', 'button_link')}),
        ("Background", {'fields': ('background_image', 'background_preview')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [ProgramInline]

    background_preview = make_image_preview('background_image', 120)


# =====================================================================
# Admissions
# =====================================================================

@admin.register(AdmissionsSection)
class AdmissionsSectionAdmin(SingletonAdmin):
    readonly_fields = ('image_preview',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Button", {'fields': ('button_text', 'button_link')}),
        ("Image", {'fields': ('image', 'image_preview', 'image_alt')}),
        ("Visibility", {'fields': ('is_active',)}),
    )

    image_preview = make_image_preview('image', 120)


# =====================================================================
# Course openings
# =====================================================================

@admin.register(OpeningsSection)
class OpeningsSectionAdmin(SingletonAdmin):
    readonly_fields = ('manage_courses',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Apply button (on every course row)", {'fields': ('apply_button_text', 'apply_button_link')}),
        ("Below the list", {'fields': ('footnote',)}),
        ("Courses", {'fields': ('manage_courses',)}),
        ("Visibility", {'fields': ('is_active',)}),
    )

    @admin.display(description="Course list")
    def manage_courses(self, obj):
        return format_html(
            '<a class="button" href="{}">Manage courses ({})</a>&nbsp; '
            '<a class="button" href="{}">+ Add new course</a>',
            reverse('admin:website_courseopening_changelist'), obj.courses.count(),
            reverse('admin:website_courseopening_add'),
        )


@admin.register(CourseOpening)
class CourseOpeningAdmin(BaseAdmin):
    list_display = ('order', 'title', 'level', 'status', 'duration', 'apply_by', 'is_active')
    list_display_links = ('title',)
    list_editable = ('order', 'status', 'apply_by', 'is_active')
    list_filter = ('level', 'status', 'is_active')
    search_fields = ('title',)
    fieldsets = (
        ("Course", {'fields': ('title', 'level', 'status')}),
        ("Details", {'fields': ('duration', 'eligibility', 'apply_by')}),
        ("Button", {'fields': ('apply_link',)}),
        ("Display", {'fields': ('order', 'is_active')}),
    )


# =====================================================================
# Research
# =====================================================================

@admin.register(ResearchSection)
class ResearchSectionAdmin(SingletonAdmin):
    readonly_fields = ('highlight_preview', 'side_preview')
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Large image card (left)", {'fields': (
            'highlight_label', 'highlight_title', 'highlight_description',
            'highlight_image', 'highlight_preview', 'highlight_image_alt')}),
        ("Small image + text (right)", {'fields': (
            'side_label', 'side_title', 'side_description',
            'side_image', 'side_preview', 'side_image_alt')}),
        ("Visibility", {'fields': ('is_active',)}),
    )

    highlight_preview = make_image_preview('highlight_image', 120)
    side_preview = make_image_preview('side_image', 120)


class ResearchTagInline(admin.TabularInline):
    model = ResearchTag
    extra = 0
    fields = ('order', 'name', 'is_active')


class ResearchFocusInline(admin.TabularInline):
    model = ResearchFocus
    extra = 0
    fields = ('order', 'label', 'title', 'description', 'is_active')


@admin.register(ResearchAreasSection)
class ResearchAreasSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [ResearchTagInline, ResearchFocusInline]


# =====================================================================
# Campus
# =====================================================================

class CampusFacilityInline(admin.TabularInline):
    model = CampusFacility
    extra = 0
    fields = ('order', 'title', 'description', 'is_active')


@admin.register(CampusSection)
class CampusSectionAdmin(SingletonAdmin):
    readonly_fields = ('image_preview',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Button", {'fields': ('button_text', 'button_link')}),
        ("Image", {'fields': ('image', 'image_preview', 'image_alt')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [CampusFacilityInline]

    image_preview = make_image_preview('image', 120)


# =====================================================================
# Gallery
# =====================================================================

class GalleryCategoryInline(admin.TabularInline):
    model = GalleryCategory
    extra = 0
    fields = ('order', 'name', 'slug', 'is_active')
    readonly_fields = ('slug',)


@admin.register(GallerySection)
class GallerySectionAdmin(SingletonAdmin):
    readonly_fields = ('manage_photos',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Filter buttons", {'fields': ('show_filters', 'all_filter_label')}),
        ("Photos", {'fields': ('manage_photos',)}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [GalleryCategoryInline]

    @admin.display(description="Photo list")
    def manage_photos(self, obj):
        return format_html(
            '<a class="button" href="{}">Manage photos ({})</a>&nbsp; '
            '<a class="button" href="{}">+ Add new photo</a>',
            reverse('admin:website_galleryimage_changelist'), obj.images.count(),
            reverse('admin:website_galleryimage_add'),
        )


@admin.register(GalleryImage)
class GalleryImageAdmin(BaseAdmin):
    list_display = ('thumbnail', 'title', 'category', 'size', 'order', 'is_active')
    list_display_links = ('thumbnail', 'title')
    list_editable = ('category', 'size', 'order', 'is_active')
    list_filter = ('category', 'size', 'is_active')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('image_preview',)
    fieldsets = (
        ("Photo", {'fields': ('image', 'image_preview')}),
        ("Caption", {'fields': ('title', 'category')}),
        ("SEO / accessibility", {'fields': ('alt_text', 'description')}),
        ("Layout", {'fields': ('size', 'order', 'is_active')}),
    )

    image_preview = make_image_preview('image', 160)
    thumbnail = make_image_preview('image', 50)


# =====================================================================
# Apply section + submitted applications
# =====================================================================

class ApplyPointInline(admin.TabularInline):
    model = ApplyPoint
    extra = 0
    fields = ('order', 'text', 'is_active')


@admin.register(ApplySection)
class ApplySectionAdmin(SingletonAdmin):
    readonly_fields = ('view_applications',)
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Form labels & placeholders", {'fields': (
            ('name_label', 'name_placeholder'),
            ('email_label', 'email_placeholder'),
            ('phone_label', 'phone_placeholder'),
            ('program_label', 'program_placeholder'),
            ('qualification_label', 'qualification_placeholder'),
            ('year_label', 'year_placeholder'),
            ('goals_label', 'goals_placeholder'),
            'consent_text', 'submit_text',
        ), 'description': "The Program dropdown lists the visible, not-closed courses from "
                          "“Courses (Course Openings list)”."}),
        ("After submit", {'fields': ('success_message', 'send_confirmation_email')}),
        ("Submissions", {'fields': ('view_applications',)}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [ApplyPointInline]

    @admin.display(description="Applications")
    def view_applications(self, obj):
        new = Application.objects.filter(status=Application.NEW).count()
        return format_html('<a class="button" href="{}">View applications ({} new)</a>',
                           reverse('admin:website_application_changelist'), new)


def export_as_csv(fields):
    """Admin action: download the selected rows as a CSV file (opens in Excel)."""
    @admin.action(description="Export selected to CSV (Excel)")
    def action(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        stamp = timezone.localtime().strftime('%Y-%m-%d')
        response['Content-Disposition'] = f'attachment; filename="{opts.model_name}s-{stamp}.csv"'
        response.write('﻿')  # BOM so Excel shows Tamil / special characters correctly
        writer = csv.writer(response)
        writer.writerow([opts.get_field(f).verbose_name.title() for f in fields])
        for obj in queryset:
            row = []
            for f in fields:
                value = getattr(obj, f)
                if f == 'status':
                    value = obj.get_status_display()
                elif hasattr(value, 'strftime'):
                    value = timezone.localtime(value).strftime('%d %b %Y %H:%M')
                row.append(value)
            writer.writerow(row)
        return response
    return action


class SubmissionAdmin(BaseAdmin):
    """Submissions come from the website: no adding in admin, visitor data is read-only."""
    list_per_page = 50
    # No date_hierarchy: it needs MySQL time-zone tables (not installed on Windows by default).
    # The "created_at" list filter (Today / Past 7 days / This month) is used instead.

    def has_add_permission(self, request):
        return False

    @admin.display(description="Received", ordering='created_at')
    def received(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d %b %Y, %I:%M %p')


@admin.register(Application)
class ApplicationAdmin(SubmissionAdmin):
    list_display = ('received', 'full_name', 'program_name', 'phone', 'email', 'status')
    list_display_links = ('received', 'full_name')
    list_editable = ('status',)
    list_filter = ('status', 'program', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'program_name')
    readonly_fields = ('full_name', 'email', 'phone', 'program', 'program_name', 'qualification',
                       'year_of_passing', 'goals', 'consent', 'ip_address', 'created_at')
    fieldsets = (
        ("Applicant", {'fields': ('full_name', 'email', 'phone')}),
        ("Program", {'fields': ('program_name', 'program', 'qualification', 'year_of_passing', 'goals')}),
        ("Follow-up (admissions team)", {'fields': ('status', 'notes')}),
        ("Technical", {'fields': ('consent', 'ip_address', 'created_at'), 'classes': ('collapse',)}),
    )
    actions = [export_as_csv(['created_at', 'full_name', 'email', 'phone', 'program_name', 'qualification',
                              'year_of_passing', 'goals', 'status', 'notes'])]


# =====================================================================
# FAQ
# =====================================================================

class FaqItemInline(admin.StackedInline):
    model = FaqItem
    extra = 0
    fields = (('order', 'is_active'), 'question', 'answer')


@admin.register(FaqSection)
class FaqSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [FaqItemInline]


# =====================================================================
# Contact section + submitted messages
# =====================================================================

class ContactSubjectInline(admin.TabularInline):
    model = ContactSubject
    extra = 0
    fields = ('order', 'name', 'is_active')


@admin.register(ContactSection)
class ContactSectionAdmin(SingletonAdmin):
    readonly_fields = ('background_preview', 'contact_details', 'view_messages')
    fieldsets = (
        ("Heading", {'fields': ('eyebrow', 'title', 'description')}),
        ("Contact details", {'fields': ('show_contact_details', 'contact_details')}),
        ("Background", {'fields': ('background_image', 'background_preview')}),
        ("Form placeholders", {'fields': (
            ('name_placeholder', 'email_placeholder'),
            ('phone_placeholder', 'subject_placeholder'),
            'message_placeholder', 'submit_text')}),
        ("After submit", {'fields': ('success_message', 'send_confirmation_email')}),
        ("Submissions", {'fields': ('view_messages',)}),
        ("Visibility", {'fields': ('is_active',)}),
    )
    inlines = [ContactSubjectInline]

    background_preview = make_image_preview('background_image', 120)

    @admin.display(description="Shown details")
    def contact_details(self, obj):
        site = SiteSettings.load()
        return format_html('{}<br>{}<br>{}<br><a href="{}">Edit in Site Settings</a>',
                           site.address, site.email, site.phone,
                           reverse('admin:website_sitesettings_change', args=[site.pk]))

    @admin.display(description="Messages")
    def view_messages(self, obj):
        new = ContactMessage.objects.filter(status=ContactMessage.NEW).count()
        return format_html('<a class="button" href="{}">View messages ({} new)</a>',
                           reverse('admin:website_contactmessage_changelist'), new)


@admin.register(ContactMessage)
class ContactMessageAdmin(SubmissionAdmin):
    list_display = ('received', 'name', 'subject_name', 'phone', 'email', 'status')
    list_display_links = ('received', 'name')
    list_editable = ('status',)
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'subject_name', 'message', 'ip_address', 'created_at')
    fieldsets = (
        ("Visitor", {'fields': ('name', 'email', 'phone')}),
        ("Message", {'fields': ('subject_name', 'message')}),
        ("Follow-up", {'fields': ('status', 'notes')}),
        ("Technical", {'fields': ('subject', 'ip_address', 'created_at'), 'classes': ('collapse',)}),
    )
    actions = [export_as_csv(['created_at', 'name', 'email', 'phone', 'subject_name', 'message', 'status', 'notes'])]


# =====================================================================
# CTA banner
# =====================================================================

@admin.register(CtaSection)
class CtaSectionAdmin(SingletonAdmin):
    readonly_fields = ('background_preview',)
    fieldsets = (
        ("Heading", {'fields': ('badge', 'title', 'description')}),
        ("Buttons", {'fields': (('primary_button_text', 'primary_button_link'),
                                ('secondary_button_text', 'secondary_button_link'))}),
        ("Background", {'fields': ('background_image', 'background_preview')}),
        ("Visibility", {'fields': ('is_active',)}),
    )

    background_preview = make_image_preview('background_image', 120)


# =====================================================================
# Footer
# =====================================================================

class FooterLinkInline(admin.TabularInline):
    extra = 0
    fields = ('order', 'label', 'link', 'open_in_new_tab', 'is_active')


class QuickLinkInline(FooterLinkInline):
    model = QuickLink
    verbose_name_plural = "Quick Links column"


class ProgramLinkInline(FooterLinkInline):
    model = ProgramLink
    verbose_name_plural = "Academic Programs column"


class LegalLinkInline(FooterLinkInline):
    model = LegalLink
    verbose_name_plural = "Bottom bar links (Privacy Policy, Terms, ...)"


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    fields = ('order', 'platform', 'url', 'is_active')
    verbose_name_plural = "Social media icons (Official Channels)"


@admin.register(Footer)
class FooterAdmin(SingletonAdmin):
    readonly_fields = ('logo_preview', 'contact_details')
    fieldsets = (
        ("Brand column", {'fields': ('logo', 'logo_preview', 'name', 'tagline', 'about_text')}),
        ("Contact lines", {'fields': ('show_contact_details', ('address_label', 'phone_label', 'email_label'),
                                      'contact_details')}),
        ("Column headings", {'fields': ('quick_links_heading', 'programs_heading', 'channels_heading',
                                        'channels_text')}),
        ("Office info (under social icons)", {'fields': ('office_title', 'office_hours')}),
        ("Bottom bar", {'fields': ('copyright_text',)}),
    )
    inlines = [QuickLinkInline, ProgramLinkInline, SocialLinkInline, LegalLinkInline]

    logo_preview = make_image_preview('logo')

    @admin.display(description="Values shown")
    def contact_details(self, obj):
        site = SiteSettings.load()
        return format_html('{} {}<br>{} {}<br>{} {}<br><a href="{}">Edit in Site Settings</a>',
                           obj.address_label, site.address, obj.phone_label, site.phone,
                           obj.email_label, site.email,
                           reverse('admin:website_sitesettings_change', args=[site.pk]))
