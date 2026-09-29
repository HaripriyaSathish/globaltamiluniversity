import os

from django.db import models
from django.utils.text import slugify


ICON_HELP = ('Outline icon name: graduation-cap, book-open, library, briefcase, school, microscope '
             '— or any Font Awesome class, e.g. "fa-solid fa-flask" (fontawesome.com/icons).')


# =====================================================================
# Base classes
# =====================================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SingletonModel(TimeStampedModel):
    """A model that can only ever have one row (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singletons are never deleted, only edited.
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OrderedItem(TimeStampedModel):
    """Repeatable item that can be sorted and hidden from admin."""
    order = models.PositiveIntegerField(default=0,
                                        help_text="Lower numbers show first. Leave 0 to add at the end.")
    is_active = models.BooleanField(default=True, help_text="Untick to hide on the website.")

    class Meta:
        abstract = True
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        # New items with no order go to the end of their list.
        if not self.order:
            siblings = type(self).objects.exclude(pk=self.pk)
            parent = next((f for f in self._meta.fields if isinstance(f, models.ForeignKey)), None)
            if parent:
                siblings = siblings.filter(**{parent.attname: getattr(self, parent.attname)})
            self.order = (siblings.aggregate(m=models.Max('order'))['m'] or 0) + 1
        super().save(*args, **kwargs)


# =====================================================================
# Site-wide settings: SEO, branding, contact details (used by topbar,
# floating buttons, contact and footer sections)
# =====================================================================

class SiteSettings(SingletonModel):
    # --- SEO ---
    meta_title = models.CharField(max_length=70, help_text="Browser tab title (max ~60–70 chars).")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Shown in Google results (max ~160 chars).")
    meta_keywords = models.CharField(max_length=300, blank=True, help_text="Comma separated.")
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True,
                                 help_text="Preview image when the link is shared (1200×630).")
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)

    # --- Branding ---
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    university_name = models.CharField(max_length=100)
    established_text = models.CharField(max_length=100, blank=True, help_text='e.g. "Est. 2001 · Coimbatore"')

    # --- Contact details ---
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True, help_text="As displayed, e.g. +91 422 123 4567")
    whatsapp_number = models.CharField(max_length=20, blank=True,
                                       help_text="Digits with country code, no + or spaces, e.g. 914221234567")

    # --- Top bar ---
    show_topbar = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Settings (SEO, Logo, Contact, Top Bar)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "Site Settings"

    @property
    def phone_link(self):
        return 'tel:' + ''.join(c for c in self.phone if c.isdigit() or c == '+')

    @property
    def whatsapp_link(self):
        return f'https://wa.me/{self.whatsapp_number}' if self.whatsapp_number else ''


# =====================================================================
# Navbar
# =====================================================================

class Navbar(SingletonModel):
    cta_text = models.CharField("Button text", max_length=50, blank=True)
    cta_link = models.CharField("Button link", max_length=255, blank=True, help_text="e.g. #admissions or a full URL")
    is_sticky = models.BooleanField(default=True, help_text="Keep the navbar fixed at the top while scrolling.")

    class Meta:
        verbose_name = "Navbar"
        verbose_name_plural = "Navbar"

    def __str__(self):
        return "Navbar"


class NavMenuItem(OrderedItem):
    navbar = models.ForeignKey(Navbar, on_delete=models.CASCADE, related_name='items')
    label = models.CharField(max_length=50)
    link = models.CharField(max_length=255, help_text="Section anchor like #about, or a full URL.")
    open_in_new_tab = models.BooleanField(default=False)

    class Meta(OrderedItem.Meta):
        verbose_name = "Menu item"

    def __str__(self):
        return self.label


# =====================================================================
# Hero section
# =====================================================================

class HeroSection(SingletonModel):
    title_line_1 = models.CharField(max_length=100, help_text='First line, e.g. "Global Tamil"')
    title_highlight = models.CharField(max_length=100, blank=True, help_text='Second line in yellow, e.g. "University"')
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=255, blank=True)
    background_image = models.ImageField(upload_to='hero/', blank=True, null=True,
                                         help_text="Recommended 1920×1080 or larger.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return "Hero Section"


class HeroTagWord(OrderedItem):
    """Small words above the title: TRADITION | KNOWLEDGE | TOMORROW"""
    hero = models.ForeignKey(HeroSection, on_delete=models.CASCADE, related_name='tag_words')
    text = models.CharField(max_length=30)

    class Meta(OrderedItem.Meta):
        verbose_name = "Tag word"

    def __str__(self):
        return self.text


# =====================================================================
# Floating buttons (right side)
# =====================================================================

class FloatingButton(OrderedItem):
    WHATSAPP, EMAIL, PHONE, CUSTOM = 'whatsapp', 'email', 'phone', 'custom'
    TYPE_CHOICES = [
        (WHATSAPP, 'WhatsApp'),
        (EMAIL, 'Email'),
        (PHONE, 'Phone call'),
        (CUSTOM, 'Custom link'),
    ]

    button_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    label = models.CharField(max_length=50, help_text="Tooltip / accessibility text.")
    link = models.CharField(max_length=255, blank=True,
                            help_text="Leave empty to use the WhatsApp / email / phone from Site Settings.")
    open_in_new_tab = models.BooleanField(default=False)

    class Meta(OrderedItem.Meta):
        verbose_name = "Floating button"

    def __str__(self):
        return self.label

    def get_href(self, site=None):
        if self.link:
            return self.link
        site = site or SiteSettings.load()
        return {
            self.WHATSAPP: site.whatsapp_link,
            self.EMAIL: f'mailto:{site.email}' if site.email else '',
            self.PHONE: site.phone_link if site.phone else '',
        }.get(self.button_type, '')


# =====================================================================
# About section
# =====================================================================

class AboutSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True,
                               help_text='Yellow text above the title, e.g. "ABOUT GLOBAL TAMIL UNIVERSITY"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Recommended 1200×700.")
    image_alt = models.CharField(max_length=150, blank=True, help_text="Describe the image (for SEO and screen readers).")
    link_text = models.CharField(max_length=50, blank=True)
    link_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Section"

    def __str__(self):
        return "About Section"


class AboutFeature(OrderedItem):
    """Feature cards: Quality Education, Research & Innovation, ..."""
    about = models.ForeignKey(AboutSection, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=100, blank=True, help_text=ICON_HELP)

    class Meta(OrderedItem.Meta):
        verbose_name = "Feature"

    def __str__(self):
        return self.title


# =====================================================================
# Academics section
# =====================================================================

class AcademicsSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True,
                               help_text='Text above the title, e.g. "OUR ACADEMICS"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=255, blank=True)
    background_image = models.ImageField(upload_to='academics/', blank=True, null=True,
                                         help_text="Faded classroom background. Recommended 1920×1080.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Academics Section"
        verbose_name_plural = "Academics Section"

    def __str__(self):
        return "Academics Section"


class Program(OrderedItem):
    """Program cards: B.A. Tamil Literature, B.Sc. Computer Science, ..."""
    academics = models.ForeignKey(AcademicsSection, on_delete=models.CASCADE, related_name='programs')
    title = models.CharField(max_length=150)
    duration = models.CharField(max_length=50, blank=True, help_text='e.g. "3 Years". Leave empty if not shown.')
    subjects = models.CharField(max_length=255, blank=True,
                                help_text='e.g. "Literature, Linguistics, Classical Tamil"')
    icon_class = models.CharField(max_length=100, blank=True, help_text=ICON_HELP)

    class Meta(OrderedItem.Meta):
        verbose_name = "Program"

    def __str__(self):
        return self.title

    @property
    def details(self):
        """Card text: '3 Years · Literature, Linguistics, Classical Tamil'"""
        return ' · '.join(part for part in (self.duration, self.subjects) if part)


# =====================================================================
# Admissions section
# =====================================================================

class AdmissionsSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True,
                               help_text='Text above the title, e.g. "ADMISSIONS"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=255, blank=True, help_text='e.g. "#contact" to scroll to the contact section.')
    image = models.ImageField(upload_to='admissions/', blank=True, null=True, help_text="Recommended 1200×700.")
    image_alt = models.CharField(max_length=150, blank=True, help_text="Describe the image (for SEO and screen readers).")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Admissions Section"
        verbose_name_plural = "Admissions Section"

    def __str__(self):
        return "Admissions Section"


# =====================================================================
# Course openings section ("Find Your Place Here")
# =====================================================================

class OpeningsSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True,
                               help_text='e.g. "CURRENT OPENINGS · 2026–27 INTAKE"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    apply_button_text = models.CharField(max_length=50, blank=True, default="Apply Now",
                                         help_text="Button text on every course row.")
    apply_button_link = models.CharField(max_length=255, blank=True, default="#contact",
                                         help_text="Default link for every course row's button.")
    footnote = models.CharField(max_length=300, blank=True, help_text="Small note shown below the course list.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Course Openings Section"
        verbose_name_plural = "Course Openings Section"

    def __str__(self):
        return "Course Openings Section"


class CourseOpening(OrderedItem):
    UNDERGRADUATE, POSTGRADUATE, DOCTORAL, DIPLOMA = 'undergraduate', 'postgraduate', 'doctoral', 'diploma'
    LEVEL_CHOICES = [
        (UNDERGRADUATE, 'Undergraduate'),
        (POSTGRADUATE, 'Postgraduate'),
        (DOCTORAL, 'Doctoral'),
        (DIPLOMA, 'Diploma'),
    ]

    OPEN, FILLING_FAST, CLOSING_SOON, CLOSED = 'open', 'filling_fast', 'closing_soon', 'closed'
    STATUS_CHOICES = [
        (OPEN, 'Open'),                   # green badge
        (FILLING_FAST, 'Filling Fast'),   # yellow badge
        (CLOSING_SOON, 'Closing Soon'),   # red badge
        (CLOSED, 'Closed'),               # grey badge
    ]

    section = models.ForeignKey(OpeningsSection, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    duration = models.CharField(max_length=50, help_text='e.g. "3 years" or "As per research plan"')
    eligibility = models.CharField(max_length=150)
    apply_by = models.DateField(null=True, blank=True, help_text="Last date to apply. Shown as e.g. 20 Oct 2026.")
    apply_link = models.CharField(max_length=255, blank=True,
                                  help_text="Leave empty to use the section's default button link.")

    class Meta(OrderedItem.Meta):
        verbose_name = "Course"
        verbose_name_plural = "Courses (Course Openings list)"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section = OpeningsSection.load()
        super().save(*args, **kwargs)

    def get_apply_link(self):
        return self.apply_link or self.section.apply_button_link


# =====================================================================
# Research section (dark blue: "Inquiry rooted in culture.")
# =====================================================================

class ResearchSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "RESEARCH AT GTU"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)

    # Large image card (left)
    highlight_label = models.CharField("Label", max_length=100, blank=True, help_text='e.g. "RESEARCH HIGHLIGHT"')
    highlight_title = models.CharField("Title", max_length=200, blank=True)
    highlight_description = models.TextField("Description", blank=True)
    highlight_image = models.ImageField("Image", upload_to='research/', blank=True, null=True,
                                        help_text="Large image. Recommended 1400×900.")
    highlight_image_alt = models.CharField("Image alt text", max_length=150, blank=True)

    # Small image + text (right)
    side_label = models.CharField("Label", max_length=100, blank=True, help_text='e.g. "FACULTY RESEARCH"')
    side_title = models.CharField("Title", max_length=200, blank=True)
    side_description = models.TextField("Description", blank=True)
    side_image = models.ImageField("Image", upload_to='research/', blank=True, null=True,
                                   help_text="Recommended 900×650.")
    side_image_alt = models.CharField("Image alt text", max_length=150, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Research Section"
        verbose_name_plural = "Research Section"

    def __str__(self):
        return "Research Section"


# =====================================================================
# Research areas section (white: "Questions Worth Exploring")
# =====================================================================

class ResearchAreasSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "RESEARCH AREAS"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Research Areas Section"
        verbose_name_plural = "Research Areas Section"

    def __str__(self):
        return "Research Areas Section"


class ResearchTag(OrderedItem):
    """Bordered tags: Tamil literature, Linguistics, ..."""
    section = models.ForeignKey(ResearchAreasSection, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=60)

    class Meta(OrderedItem.Meta):
        verbose_name = "Tag"

    def __str__(self):
        return self.name


class ResearchFocus(OrderedItem):
    """Numbered list on the right: 01 / CURRENT RESEARCH PROJECTS ..."""
    section = models.ForeignKey(ResearchAreasSection, on_delete=models.CASCADE, related_name='focus_items')
    label = models.CharField(max_length=100, help_text='e.g. "CURRENT RESEARCH PROJECTS" (number is added automatically)')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta(OrderedItem.Meta):
        verbose_name = "Focus item"
        verbose_name_plural = "Focus items"

    def __str__(self):
        return self.title


# =====================================================================
# Campus section ("A Green Campus for Great Minds")
# =====================================================================

class CampusSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "OUR CAMPUS"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=255, blank=True, help_text='e.g. "#gallery" to scroll to the gallery section.')
    image = models.ImageField(upload_to='campus/', blank=True, null=True, help_text="Recommended 1400×800.")
    image_alt = models.CharField(max_length=150, blank=True, help_text="Describe the image (for SEO and screen readers).")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Campus Section"
        verbose_name_plural = "Campus Section"

    def __str__(self):
        return "Campus Section"


class CampusFacility(OrderedItem):
    """Numbered facility cards: 01 Smart Classrooms, 02 Central Library, ..."""
    section = models.ForeignKey(CampusSection, on_delete=models.CASCADE, related_name='facilities')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta(OrderedItem.Meta):
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.title


# =====================================================================
# Gallery section ("Life on Campus")
# =====================================================================

class GallerySection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "COLLEGE GALLERY"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    show_filters = models.BooleanField(default=True, help_text="Show the category filter buttons above the photos.")
    all_filter_label = models.CharField(max_length=30, default="All", help_text='Text of the first filter button.')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gallery Section"
        verbose_name_plural = "Gallery Section"

    def __str__(self):
        return "Gallery Section"


class GalleryCategory(OrderedItem):
    """Filter buttons / yellow labels: Campus, Academics, Labs, Student Life, Events"""
    section = models.ForeignKey(GallerySection, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True,
                            help_text="Used by the filter buttons. Filled automatically from the name.")

    class Meta(OrderedItem.Meta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section = GallerySection.load()
        if not self.slug:
            base = slugify(self.name) or 'category'
            slug, n = base, 2
            while GalleryCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f'{base}-{n}', n + 1
            self.slug = slug
        super().save(*args, **kwargs)


def gallery_upload_to(instance, filename):
    """Give uploaded photos a readable name: gallery/<category>/<title>.jpg"""
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    folder = instance.category.slug if instance.category_id else 'general'
    return f'gallery/{folder}/{slugify(instance.title) or "photo"}{ext}'


class GalleryImage(OrderedItem):
    NORMAL, WIDE, TALL, FULL = 'normal', 'wide', 'tall', 'full'
    SIZE_CHOICES = [
        (NORMAL, 'Normal (1 column)'),
        (WIDE, 'Wide (2 columns)'),
        (TALL, 'Tall (2 rows)'),
        (FULL, 'Full width (whole row)'),
    ]

    section = models.ForeignKey(GallerySection, on_delete=models.CASCADE, related_name='images')
    category = models.ForeignKey(GalleryCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='images', help_text="Yellow label on the photo and filter group.")
    title = models.CharField(max_length=150, help_text='White caption on the photo, e.g. "Learning together"')
    image = models.ImageField(upload_to=gallery_upload_to, blank=True, null=True,
                              help_text="The file is renamed from the category and title "
                                        "(e.g. gallery/labs/discovery-in-practice). "
                                        "Large photos are compressed automatically.")
    alt_text = models.CharField(max_length=200, blank=True,
                                help_text="Describe what is in the photo (SEO & screen readers). "
                                          "Leave empty to create it from the title and category.")
    description = models.TextField(blank=True, help_text="Optional longer description (shown when the photo is opened).")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default=NORMAL,
                            help_text="How much space the photo takes in the grid.")

    class Meta(OrderedItem.Meta):
        verbose_name = "Gallery photo"
        verbose_name_plural = "Gallery photos"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section = GallerySection.load()
        if not self.alt_text:
            parts = [self.title, self.category.name if self.category_id else '', "Global Tamil University"]
            self.alt_text = ' – '.join(p for p in parts if p)
        super().save(*args, **kwargs)


# =====================================================================
# Apply section ("Start Your Application") + submitted applications
# =====================================================================

class ApplySection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "APPLY TO GTU"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)

    # Form labels & placeholders
    name_label = models.CharField(max_length=60, default="Full Name")
    name_placeholder = models.CharField(max_length=100, blank=True)
    email_label = models.CharField(max_length=60, default="Email Address")
    email_placeholder = models.CharField(max_length=100, blank=True)
    phone_label = models.CharField(max_length=60, default="Phone Number")
    phone_placeholder = models.CharField(max_length=100, blank=True)
    program_label = models.CharField(max_length=60, default="Program of Interest")
    program_placeholder = models.CharField(max_length=100, blank=True, help_text="First (empty) option of the dropdown.")
    qualification_label = models.CharField(max_length=60, default="Highest Qualification")
    qualification_placeholder = models.CharField(max_length=100, blank=True)
    year_label = models.CharField(max_length=60, default="Year of Passing")
    year_placeholder = models.CharField(max_length=100, blank=True)
    goals_label = models.CharField(max_length=60, default="Tell us about your goals")
    goals_placeholder = models.CharField(max_length=200, blank=True)
    consent_text = models.CharField(max_length=200, blank=True)
    submit_text = models.CharField("Submit button text", max_length=50, default="Submit Application")

    # After submit
    success_message = models.CharField(max_length=300, help_text="Shown to the visitor after a successful submit.")
    send_confirmation_email = models.BooleanField(default=True,
                                                  help_text="Email the applicant an acknowledgement.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Apply Section (application form)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "Apply Section"


class ApplyPoint(OrderedItem):
    """Check-mark points: Applications reviewed by our admissions team, ..."""
    section = models.ForeignKey(ApplySection, on_delete=models.CASCADE, related_name='points')
    text = models.CharField(max_length=150)

    class Meta(OrderedItem.Meta):
        verbose_name = "Point"

    def __str__(self):
        return self.text


class Application(TimeStampedModel):
    NEW, CONTACTED, IN_REVIEW, ADMITTED, NOT_ADMITTED = 'new', 'contacted', 'in_review', 'admitted', 'not_admitted'
    STATUS_CHOICES = [
        (NEW, 'New'),
        (CONTACTED, 'Contacted'),
        (IN_REVIEW, 'In review'),
        (ADMITTED, 'Admitted'),
        (NOT_ADMITTED, 'Not admitted'),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    program = models.ForeignKey(CourseOpening, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='applications')
    program_name = models.CharField(max_length=150, blank=True,
                                    help_text="Program title at the time of applying (kept even if the course is deleted).")
    qualification = models.CharField("Highest qualification", max_length=120)
    year_of_passing = models.PositiveSmallIntegerField()
    goals = models.TextField(blank=True)
    consent = models.BooleanField(default=False)

    # Admin tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    notes = models.TextField("Internal notes", blank=True, help_text="Only visible in admin.")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Application"
        verbose_name_plural = "Applications (submitted)"

    def __str__(self):
        return f"{self.full_name} – {self.program_name or 'No program'}"

    def save(self, *args, **kwargs):
        if self.program_id and not self.program_name:
            self.program_name = self.program.title
        super().save(*args, **kwargs)


# =====================================================================
# FAQ section ("Frequently Asked Questions") – shown before Contact
# =====================================================================

class FaqSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "FAQ"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FAQ Section"
        verbose_name_plural = "FAQ Section"

    def __str__(self):
        return "FAQ Section"


class FaqItem(OrderedItem):
    """One question + answer. Also added to Google's FAQ structured data."""
    section = models.ForeignKey(FaqSection, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta(OrderedItem.Meta):
        verbose_name = "Question"

    def __str__(self):
        return self.question


# =====================================================================
# Contact section ("Contact Us") + submitted messages
# =====================================================================

class ContactSection(SingletonModel):
    eyebrow = models.CharField("Small heading", max_length=100, blank=True, help_text='e.g. "GET IN TOUCH"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    show_contact_details = models.BooleanField(default=True,
                                               help_text="Show address, email and phone (from Site Settings).")
    background_image = models.ImageField(upload_to='contact/', blank=True, null=True,
                                         help_text="Shown behind a blue overlay. Recommended 1920×1080.")

    # Form placeholders
    name_placeholder = models.CharField(max_length=60, default="Name")
    email_placeholder = models.CharField(max_length=60, default="Email")
    phone_placeholder = models.CharField(max_length=60, default="Phone")
    subject_placeholder = models.CharField(max_length=60, default="Select Subject",
                                           help_text="First (empty) option of the subject dropdown.")
    message_placeholder = models.CharField(max_length=100, default="Message")
    submit_text = models.CharField("Submit button text", max_length=50, default="Send Message")

    success_message = models.CharField(max_length=300, help_text="Shown to the visitor after a successful submit.")
    send_confirmation_email = models.BooleanField(default=True,
                                                  help_text="Email the visitor an acknowledgement.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact Section (contact form)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "Contact Section"


class ContactSubject(OrderedItem):
    """Options of the 'Select Subject' dropdown."""
    section = models.ForeignKey(ContactSection, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=80)

    class Meta(OrderedItem.Meta):
        verbose_name = "Subject option"

    def __str__(self):
        return self.name


class ContactMessage(TimeStampedModel):
    NEW, REPLIED, CLOSED = 'new', 'replied', 'closed'
    STATUS_CHOICES = [(NEW, 'New'), (REPLIED, 'Replied'), (CLOSED, 'Closed')]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.ForeignKey(ContactSubject, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='messages')
    subject_name = models.CharField(max_length=80, blank=True,
                                    help_text="Subject at the time of sending (kept even if the option is deleted).")
    message = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    notes = models.TextField("Internal notes", blank=True, help_text="Only visible in admin.")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact message"
        verbose_name_plural = "Contact messages (submitted)"

    def __str__(self):
        return f"{self.name} – {self.subject_name or 'General'}"

    def save(self, *args, **kwargs):
        if self.subject_id and not self.subject_name:
            self.subject_name = self.subject.name
        super().save(*args, **kwargs)


# =====================================================================
# CTA banner ("Your Future Starts Here.")
# =====================================================================

class CtaSection(SingletonModel):
    badge = models.CharField(max_length=60, blank=True, help_text='Yellow badge, e.g. "ADMISSIONS CYCLE 2026–27"')
    title = models.TextField(max_length=200, help_text="Press Enter to start a new line.")
    description = models.TextField(blank=True)
    primary_button_text = models.CharField("Yellow button text", max_length=50, blank=True)
    primary_button_link = models.CharField("Yellow button link", max_length=255, blank=True)
    secondary_button_text = models.CharField("White button text", max_length=50, blank=True)
    secondary_button_link = models.CharField("White button link", max_length=255, blank=True)
    background_image = models.ImageField(upload_to='cta/', blank=True, null=True,
                                         help_text="Shown behind a blue overlay. Recommended 1920×1080.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "CTA Banner (Your Future Starts Here)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "CTA Banner"


# =====================================================================
# Footer
# =====================================================================

class Footer(SingletonModel):
    # Brand column
    logo = models.ImageField(upload_to='branding/', blank=True, null=True,
                             help_text="Optional. Leave empty to use the logo from Site Settings.")
    name = models.CharField(max_length=100, blank=True,
                            help_text="Leave empty to use the university name from Site Settings.")
    tagline = models.CharField(max_length=100, blank=True, help_text='e.g. "ESTABLISHED 2001 • COIMBATORE"')
    about_text = models.TextField(blank=True)

    # Contact lines (values come from Site Settings)
    show_contact_details = models.BooleanField(default=True)
    address_label = models.CharField(max_length=30, default="Campus:")
    phone_label = models.CharField(max_length=30, default="Telephone:")
    email_label = models.CharField(max_length=30, default="Email:")

    # Column headings
    quick_links_heading = models.CharField(max_length=60, default="Quick Links")
    programs_heading = models.CharField(max_length=60, default="Academic Programs")
    channels_heading = models.CharField(max_length=60, default="Official Channels")
    channels_text = models.TextField(blank=True, help_text="Text above the social media icons.")

    # Office info (under the social icons)
    office_title = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=150, blank=True)

    # Bottom bar
    copyright_text = models.CharField(max_length=200, blank=True,
                                      help_text='Use {year} for the current year, e.g. "© {year} Global Tamil University. '
                                                'All Rights Reserved."')

    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footer"

    def __str__(self):
        return "Footer"

    @property
    def copyright(self):
        from django.utils import timezone
        return self.copyright_text.replace('{year}', str(timezone.localdate().year))


class FooterLink(OrderedItem):
    QUICK, PROGRAMS, LEGAL = 'quick', 'programs', 'legal'
    COLUMN_CHOICES = [
        (QUICK, 'Quick Links'),
        (PROGRAMS, 'Academic Programs'),
        (LEGAL, 'Bottom bar (legal)'),
    ]

    footer = models.ForeignKey(Footer, on_delete=models.CASCADE, related_name='links')
    column = models.CharField(max_length=20, choices=COLUMN_CHOICES)
    label = models.CharField(max_length=100)
    link = models.CharField(max_length=255, help_text="Section anchor like #about, or a full URL.")
    open_in_new_tab = models.BooleanField(default=False)

    class Meta(OrderedItem.Meta):
        ordering = ['column', 'order', 'id']
        verbose_name = "Footer link"

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        column = getattr(type(self), 'COLUMN', None)
        if column:
            self.column = column
        if not self.order:
            # number within its own column
            last = FooterLink.objects.filter(footer_id=self.footer_id, column=self.column) \
                .exclude(pk=self.pk).aggregate(m=models.Max('order'))['m']
            self.order = (last or 0) + 1
        super().save(*args, **kwargs)


class _ColumnManager(models.Manager):
    def __init__(self, column):
        super().__init__()
        self.column = column

    def get_queryset(self):
        return super().get_queryset().filter(column=self.column)


class QuickLink(FooterLink):
    COLUMN = FooterLink.QUICK
    objects = _ColumnManager(FooterLink.QUICK)

    class Meta:
        proxy = True
        verbose_name = "Quick link"


class ProgramLink(FooterLink):
    COLUMN = FooterLink.PROGRAMS
    objects = _ColumnManager(FooterLink.PROGRAMS)

    class Meta:
        proxy = True
        verbose_name = "Academic program link"


class LegalLink(FooterLink):
    COLUMN = FooterLink.LEGAL
    objects = _ColumnManager(FooterLink.LEGAL)

    class Meta:
        proxy = True
        verbose_name = "Bottom bar link"


class SocialLink(OrderedItem):
    YOUTUBE, LINKEDIN, TWITTER, FACEBOOK, INSTAGRAM, WHATSAPP = (
        'youtube', 'linkedin', 'twitter', 'facebook', 'instagram', 'whatsapp')
    PLATFORM_CHOICES = [
        (YOUTUBE, 'YouTube'),
        (LINKEDIN, 'LinkedIn'),
        (TWITTER, 'X / Twitter'),
        (FACEBOOK, 'Facebook'),
        (INSTAGRAM, 'Instagram'),
        (WHATSAPP, 'WhatsApp'),
    ]
    ICONS = {
        YOUTUBE: 'fa-solid fa-circle-play',       # round play icon, as in the design
        LINKEDIN: 'fa-brands fa-linkedin',
        TWITTER: 'fa-brands fa-twitter',
        FACEBOOK: 'fa-brands fa-facebook-f',
        INSTAGRAM: 'fa-brands fa-instagram',
        WHATSAPP: 'fa-brands fa-whatsapp',
    }

    footer = models.ForeignKey(Footer, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField(blank=True, help_text="Full profile/channel URL. Without a URL the icon is shown but not clickable.")

    class Meta(OrderedItem.Meta):
        verbose_name = "Social media link"

    def __str__(self):
        return self.get_platform_display()

    @property
    def icon_class(self):
        return self.ICONS.get(self.platform, 'fa-solid fa-link')
