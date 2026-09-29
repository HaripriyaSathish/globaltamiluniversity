"""
Seed the website with the exact text from the design.

    python manage.py seed_data            # adds missing records and fills empty fields (keeps admin edits)
    python manage.py seed_data --reset    # overwrites text with the design text (images are never touched)

Safe to run again after new sections/fields are added.
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import (
    SiteSettings, Navbar, HeroSection, FloatingButton, AboutSection, AcademicsSection,
    AdmissionsSection, OpeningsSection, CourseOpening,
    ResearchSection, ResearchAreasSection, CampusSection, GallerySection, GalleryImage,
    ApplySection, FaqSection, ContactSection,
    CtaSection, Footer, QuickLink, ProgramLink, LegalLink, SocialLink,
)


# =====================================================================
# Seed content (exact words from the design)
# =====================================================================

SITE_SETTINGS = {
    'meta_title': "Global Tamil University, Coimbatore | Courses & Admissions",
    'meta_description': (
        "Global Tamil University in Coimbatore offers B.A. Tamil Literature, B.Sc. Computer Science, "
        "B.Com, B.Ed, M.A. Tamil Studies and Ph.D. research programmes. Explore courses and admissions."
    ),
    'meta_keywords': "Global Tamil University, Coimbatore university, Tamil university, admissions, research",
    'university_name': "GLOBAL TAMIL UNIVERSITY",
    'established_text': "Est. 2001 · Coimbatore",
    'address': "No 175, Tiru Nagar, Coimbatore – 641035",
    'email': "globalTamilcoiv@gmail.com",
    'phone': "+91 422 123 4567",
    'whatsapp_number': "914221234567",
    'show_topbar': True,
}

NAVBAR = {
    'cta_text': "Apply Now",
    'cta_link': "#admissions",
    'is_sticky': True,
}

NAV_ITEMS = [
    ("Home", "#home"),
    ("About", "#about"),
    ("Academics", "#academics"),
    ("Admissions", "#admissions"),
    ("Research", "#research"),
    ("Campus", "#campus"),
    ("Contact", "#contact"),
]

HERO = {
    'title_line_1': "Global Tamil",
    'title_highlight': "University",
    'subtitle': "Rooted in Heritage. Ready for Tomorrow.",
    'description': (
        "A university in Coimbatore connecting Tamil heritage, modern education, "
        "research and future-ready learning."
    ),
    'button_text': "Explore Our University",
    'button_link': "#about",
    'is_active': True,
}

HERO_TAG_WORDS = ["TRADITION", "KNOWLEDGE", "TOMORROW"]

# link left empty -> built from Site Settings (whatsapp / email / phone)
FLOATING_BUTTONS = [
    (FloatingButton.WHATSAPP, "Chat on WhatsApp", True),
    (FloatingButton.EMAIL, "Send us an Email", False),
    (FloatingButton.PHONE, "Call Us", False),
]

ABOUT = {
    'eyebrow': "ABOUT GLOBAL TAMIL UNIVERSITY",
    'title': "Preserving Heritage,\nBuilding Tomorrow",
    'description': (
        "Global Tamil University, established in 2001 in Coimbatore, is dedicated to "
        "providing world-class education, preserving Tamil heritage, and fostering "
        "innovation and research for a brighter future."
    ),
    'image_alt': "Students walking towards the Global Tamil University campus building",
    'link_text': "Learn More",
    'link_url': "#academics",
    'is_active': True,
}

ABOUT_FEATURES = [
    ("Quality Education", "fa-solid fa-graduation-cap"),
    ("Research & Innovation", "fa-solid fa-flask"),
    ("Holistic Development", "fa-solid fa-users"),
    ("Global Opportunities", "fa-solid fa-globe"),
]

ACADEMICS = {
    'eyebrow': "OUR ACADEMICS",
    'title': "Diverse Programs for a Brighter Future",
    'description': (
        "We offer a wide range of undergraduate, postgraduate and research programs "
        "designed to build knowledge, skills and leadership."
    ),
    'button_text': "Explore Our University",
    'button_link': "#admissions",
    'is_active': True,
}

# (title, duration, subjects, icon)
PROGRAMS = [
    ("B.A. Tamil Literature", "3 Years", "Literature, Linguistics, Classical Tamil", "graduation-cap"),
    ("B.Sc. Computer Science", "3 Years", "Programming, Data Structures, AI Fundamentals", "book-open"),
    ("M.A. Tamil Studies", "2 Years", "Advanced Tamil Literature, History & Culture", "library"),
    ("B.Com Commerce", "3 Years", "Finance, Accounting, Business Management", "briefcase"),
    ("B.Ed Education", "2 Years", "Teacher Training, Pedagogy, Educational Psychology", "school"),
    ("Ph.D. Research Programs", "", "Tamil, Linguistics, Social Sciences", "microscope"),
]

ADMISSIONS = {
    'eyebrow': "ADMISSIONS",
    'title': "Your Journey\nBegins Here",
    'description': (
        "Join a community of learners, thinkers, and leaders. Apply now and be a "
        "part of Global Tamil University."
    ),
    'button_text': "Apply Now",
    'button_link': "#openings",
    'image_alt': "Students walking to the Global Tamil University main building",
    'is_active': True,
}

OPENINGS = {
    'eyebrow': "CURRENT OPENINGS · 2026–27 INTAKE",
    'title': "Find Your Place Here",
    'description': (
        "Explore the courses accepting applications. Find the pathway that fits "
        "your ambitions and take the next step."
    ),
    'apply_button_text': "Apply Now",
    'apply_button_link': "#apply",
    'footnote': (
        "Program requirements and dates shown are indicative; confirm current "
        "admission details with the university before applying."
    ),
    'is_active': True,
}

UG, PG, PHD = CourseOpening.UNDERGRADUATE, CourseOpening.POSTGRADUATE, CourseOpening.DOCTORAL
OPEN, FILLING_FAST, CLOSING_SOON = CourseOpening.OPEN, CourseOpening.FILLING_FAST, CourseOpening.CLOSING_SOON

# (level, title, status, duration, eligibility, apply_by)
COURSE_OPENINGS = [
    (UG, "B.A. Tamil Literature", OPEN, "3 years", "Higher Secondary (10+2)", date(2026, 10, 20)),
    (UG, "B.Sc. Computer Science", FILLING_FAST, "3 years", "Higher Secondary (10+2)", date(2026, 10, 10)),
    (PG, "M.A. Tamil Studies", OPEN, "2 years", "Bachelor’s degree", date(2026, 10, 31)),
    (UG, "B.Com Commerce", CLOSING_SOON, "3 years", "Higher Secondary (10+2)", date(2026, 10, 5)),
    (UG, "B.Ed Education", OPEN, "2 years", "Bachelor’s degree", date(2026, 11, 15)),
    (PHD, "Ph.D. Research Programs", OPEN, "As per research plan", "Relevant master’s degree", date(2026, 11, 30)),
]

RESEARCH = {
    'eyebrow': "RESEARCH AT GTU",
    'title': "Inquiry rooted in culture.\nIdeas for the future.",
    'description': (
        "Our research connects the depth of Tamil scholarship with new approaches to "
        "language, society and technology — bringing scholars and students into the "
        "same conversation."
    ),
    'highlight_label': "RESEARCH HIGHLIGHT",
    'highlight_title': "Preserving Knowledge. Creating New Possibilities.",
    'highlight_description': (
        "Research in manuscripts, digital archives and Tamil studies brings historical "
        "knowledge into conversation with contemporary methods of preservation and discovery."
    ),
    'highlight_image_alt': "Researchers studying Tamil palm-leaf manuscripts on screen in the library",
    'side_label': "FACULTY RESEARCH",
    'side_title': "Scholarship across disciplines",
    'side_description': (
        "Faculty-led inquiry spans literary studies, linguistics, education and the "
        "social sciences, with opportunities for student participation."
    ),
    'side_image_alt': "Faculty and students discussing research around a table",
    'is_active': True,
}

RESEARCH_AREAS = {
    'eyebrow': "RESEARCH AREAS",
    'title': "Explore Tamil Research & PhD Programmes",
    'description': (
        "Research at Global Tamil University connects Tamil scholarship with interdisciplinary "
        "approaches to language, culture, education, society and technology."
    ),
    'is_active': True,
}

RESEARCH_TAGS = ["Tamil Literature", "Linguistics", "Digital Humanities", "Education", "Social Sciences"]

# (label, title, description)
RESEARCH_FOCUS = [
    ("CURRENT RESEARCH PROJECTS", "Manuscripts & digital archives",
     "Exploring how archival practices, transcription and digital tools can make "
     "Tamil source material more accessible for study."),
    ("PUBLICATIONS", "Sharing scholarship",
     "Research papers, critical editions and interdisciplinary writing offer ways "
     "for faculty and students to contribute to wider academic dialogue."),
    ("CONFERENCES & SEMINARS", "Ideas in conversation",
     "Scholarly talks, research presentations and seminars create space to "
     "exchange perspectives across fields and generations."),
]

CAMPUS = {
    'eyebrow': "OUR CAMPUS",
    'title': "A Green Campus\nfor Great Minds",
    'description': (
        "Experience a vibrant campus with modern infrastructure, spacious facilities "
        "and a supportive learning environment."
    ),
    'button_text': "Explore Campus",
    'button_link': "#gallery",
    'image_alt': "Aerial view of the Global Tamil University campus with gardens and palm-lined avenue",
    'is_active': True,
}

# (title, description)
CAMPUS_FACILITIES = [
    ("Smart Classrooms",
     "Acoustic amphitheaters with dual interactive displays and live lecture streaming."),
    ("Central Library",
     "120,000+ volumes, ancient palm-leaf manuscript vaults, and digital e-databases."),
    ("Computer Labs",
     "High-performance GPU rigs for neural network training and speech synthesis research."),
    ("Science Labs",
     "Specialized analytical chemistry, physics instrumentation, and cognitive test labs."),
    ("Seminar Halls",
     "Multiple climate-controlled colloquium auditoriums for international symposiums."),
    ("Cultural Spaces",
     "Open-air stone amphitheater and dedicated classical music and Natya practice halls."),
    ("Student Areas",
     "Spacious cafeteria pavilions, recreational sports arenas, and reading quadrangles."),
    ("Green Campus",
     "Solar powered, rainwater harvested micro-arboretum with native Western Ghats botanical flora."),
]

GALLERY = {
    'eyebrow': "COLLEGE GALLERY",
    'title': "Life on Campus",
    'description': (
        "A closer look at the spaces, people and moments that shape our university community."
    ),
    'show_filters': True,
    'all_filter_label': "All",
    'is_active': True,
}

GALLERY_CATEGORIES = ["Campus", "Academics", "Labs", "Student Life", "Events"]

W, T, F, N = GalleryImage.WIDE, GalleryImage.TALL, GalleryImage.FULL, GalleryImage.NORMAL

# (title, category, size, alt text) — in the order they appear in the design grid
GALLERY_IMAGES = [
    ("The campus from above", "Campus", T,
     "Aerial view of the Global Tamil University main building with palm-lined gardens and hills behind"),
    ("Learning together", "Academics", W,
     "Students discussing in a classroom while a faculty member explains"),
    ("A place to explore", "Academics", N,
     "Students reading in the wood-panelled central library"),
    ("Discovery in practice", "Labs", W,
     "Students working with a microscope and computers in the science lab"),
    ("Celebrating our heritage", "Events", T,
     "Students performing Bharatanatyam classical dance at a campus cultural event"),
    ("Beyond the classroom", "Student Life", W,
     "Students playing cricket on the campus sports ground in front of the pavilion"),
    ("Everyday campus life", "Student Life", N,
     "Students with backpacks walking together towards the main building"),
    ("A place to belong", "Campus", F,
     "Heritage façade of the main building with arched colonnades and palm trees"),
]

APPLY = {
    'eyebrow': "APPLY TO GTU",
    'title': "Start Your\nApplication",
    'description': (
        "Take the first step toward your future. Complete the form and our admissions "
        "team will contact you with the next steps."
    ),
    'name_label': "Full Name",
    'name_placeholder': "Enter your full name",
    'email_label': "Email Address",
    'email_placeholder': "you@example.com",
    'phone_label': "Phone Number",
    'phone_placeholder': "9876543210",
    'program_label': "Program of Interest",
    'program_placeholder': "Select a program",
    'qualification_label': "Highest Qualification",
    'qualification_placeholder': "e.g. Higher Secondary",
    'year_label': "Year of Passing",
    'year_placeholder': "2026",
    'goals_label': "Tell us about your goals",
    'goals_placeholder': "What would you like to achieve at GTU?",
    'consent_text': "I agree to be contacted by the admissions team.",
    'submit_text': "Submit Application",
    'success_message': (
        "Thank you! Your application has been received. Our admissions team will "
        "contact you soon with the next steps."
    ),
    'send_confirmation_email': True,
    'is_active': True,
}

APPLY_POINTS = [
    "Applications reviewed by our admissions team",
    "Guidance on programs and eligibility",
    "Simple and secure application process",
]

FAQ = {
    'eyebrow': "FAQ",
    'title': "Frequently Asked Questions",
    'is_active': True,
}

# (question, answer)
FAQ_QUESTIONS = [
    ("What programmes does Global Tamil University offer?",
     "Global Tamil University offers B.A. Tamil Literature, B.Sc. Computer Science, M.A. Tamil Studies, "
     "B.Com Commerce, B.Ed Education and Ph.D. Research Programmes."),
    ("Where is Global Tamil University located?",
     "Global Tamil University is located in Saravanampatti, Coimbatore."),
    ("How can I apply for admission?",
     "Choose your programme, review the eligibility requirements and submit the application form. "
     "The admissions team will contact you with the next steps."),
    ("What are the eligibility requirements for the programmes?",
     "B.A. Tamil Literature, B.Sc. Computer Science and B.Com Commerce require Higher Secondary (10+2). "
     "M.A. Tamil Studies and B.Ed Education require a bachelor’s degree. "
     "Ph.D. Research Programmes require a relevant master’s degree."),
    ("Does Global Tamil University offer Ph.D. research programmes?",
     "Yes. The university lists Ph.D. Research Programmes with research areas including Tamil, "
     "Linguistics and Social Sciences."),
]

CONTACT = {
    'eyebrow': "GET IN TOUCH",
    'title': "Contact Us",
    'description': (
        "We are here to help. Reach out for admissions, program details, and any other queries."
    ),
    'show_contact_details': True,
    'name_placeholder': "Name",
    'email_placeholder': "Email",
    'phone_placeholder': "Phone",
    'subject_placeholder': "Select Subject",
    'message_placeholder': "Message",
    'submit_text': "Send Message",
    'success_message': "Thank you for reaching out! Our team will get back to you shortly.",
    'send_confirmation_email': True,
    'is_active': True,
}

# Taken from the section description: "admissions, program details, and any other queries"
CONTACT_SUBJECTS = ["Admissions", "Program Details", "Other Queries"]

CTA = {
    'badge': "ADMISSIONS CYCLE 2026–27",
    'title': "Your Future Starts Here.",
    'description': (
        "Discover your program, connect with our academic community and take the "
        "next step toward your future."
    ),
    'primary_button_text': "APPLY NOW",
    'primary_button_link': "#apply",
    'secondary_button_text': "EXPLORE PROGRAMS",
    'secondary_button_link': "#academics",
    'is_active': True,
}

FOOTER = {
    'name': "GLOBAL TAMIL UNIVERSITY",
    'tagline': "ESTABLISHED 2001 • COIMBATORE",
    'about_text': (
        "Global Tamil University is an autonomous higher learning institution dedicated "
        "to the preservation of classical Tamil knowledge traditions, linguistic sciences, "
        "and frontier research in technological and societal disciplines."
    ),
    'show_contact_details': True,
    'address_label': "Campus:",
    'phone_label': "Telephone:",
    'email_label': "Email:",
    'quick_links_heading': "Quick Links",
    'programs_heading': "Academic Programs",
    'channels_heading': "Official Channels",
    'channels_text': "Follow our university dispatches, research bulletins, and cultural event broadcasts.",
    'office_title': "Coimbatore Academic Registrar",
    'office_hours': "Office hours: Mon–Fri, 9:00 AM – 5:00 PM IST",
    'copyright_text': "© {year} Global Tamil University. All Rights Reserved.",
}

FOOTER_QUICK_LINKS = [
    ("Home", "#home"),
    ("About Us", "#about"),
    ("Academics", "#academics"),
    ("Admissions", "#admissions"),
    ("Research Colloquium", "#research"),
    ("Campus Experience", "#campus"),
    ("Contact", "#contact"),
]

FOOTER_PROGRAM_LINKS = [
    ("B.A. Tamil Literature (3 Yrs)", "#academics"),
    ("B.Sc Computer Science (3 Yrs)", "#academics"),
    ("M.A. Tamil Studies (2 Yrs)", "#academics"),
    ("B.Com Commerce (3 Yrs)", "#academics"),
    ("B.Ed Education (2 Yrs)", "#academics"),
    ("Ph.D. Doctoral Research Programs", "#academics"),
]

# URLs are not in the design yet -> "#" until the pages exist
FOOTER_LEGAL_LINKS = [
    ("Privacy Policy", "#"),
    ("Terms of Use", "#"),
    ("Right to Information (RTI)", "#"),
    ("Anti-Ragging Regulations", "#"),
]

# URL left empty -> icon stays hidden until the real channel URL is added in admin
FOOTER_SOCIAL = [SocialLink.YOUTUBE, SocialLink.LINKEDIN, SocialLink.TWITTER]


# =====================================================================
# Command
# =====================================================================

class Command(BaseCommand):
    help = "Seed website content with the text from the design."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help="Overwrite existing text with the seed text (images are kept).")

    @transaction.atomic
    def handle(self, *args, reset=False, **options):
        self.reset = reset

        self.seed_singleton(SiteSettings, SITE_SETTINGS)

        navbar = self.seed_singleton(Navbar, NAVBAR)
        self.seed_items(navbar.items, [
            {'label': label, 'link': link} for label, link in NAV_ITEMS
        ], key='label')

        hero = self.seed_singleton(HeroSection, HERO)
        self.seed_items(hero.tag_words, [{'text': t} for t in HERO_TAG_WORDS], key='text')

        self.seed_items(FloatingButton.objects, [
            {'button_type': t, 'label': label, 'open_in_new_tab': new_tab}
            for t, label, new_tab in FLOATING_BUTTONS
        ], key='button_type')

        about = self.seed_singleton(AboutSection, ABOUT)
        self.seed_items(about.features, [
            {'title': title, 'icon_class': icon} for title, icon in ABOUT_FEATURES
        ], key='title')

        academics = self.seed_singleton(AcademicsSection, ACADEMICS)
        self.seed_items(academics.programs, [
            {'title': title, 'duration': duration, 'subjects': subjects, 'icon_class': icon}
            for title, duration, subjects, icon in PROGRAMS
        ], key='title')

        self.seed_singleton(AdmissionsSection, ADMISSIONS)

        openings = self.seed_singleton(OpeningsSection, OPENINGS)
        self.seed_items(openings.courses, [
            {'level': level, 'title': title, 'status': status, 'duration': duration,
             'eligibility': eligibility, 'apply_by': apply_by}
            for level, title, status, duration, eligibility, apply_by in COURSE_OPENINGS
        ], key='title')

        self.seed_singleton(ResearchSection, RESEARCH)

        research_areas = self.seed_singleton(ResearchAreasSection, RESEARCH_AREAS)
        self.seed_items(research_areas.tags, [{'name': n} for n in RESEARCH_TAGS], key='name')
        self.seed_items(research_areas.focus_items, [
            {'label': label, 'title': title, 'description': description}
            for label, title, description in RESEARCH_FOCUS
        ], key='title')

        campus = self.seed_singleton(CampusSection, CAMPUS)
        self.seed_items(campus.facilities, [
            {'title': title, 'description': description} for title, description in CAMPUS_FACILITIES
        ], key='title')

        gallery = self.seed_singleton(GallerySection, GALLERY)
        self.seed_items(gallery.categories, [{'name': n} for n in GALLERY_CATEGORIES], key='name')
        categories = {c.name: c for c in gallery.categories.all()}
        self.seed_items(gallery.images, [
            {'title': title, 'category': categories.get(category), 'size': size, 'alt_text': alt}
            for title, category, size, alt in GALLERY_IMAGES
        ], key='title')

        apply = self.seed_singleton(ApplySection, APPLY)
        self.seed_items(apply.points, [{'text': t} for t in APPLY_POINTS], key='text')

        faq = self.seed_singleton(FaqSection, FAQ)
        self.seed_items(faq.questions, [
            {'question': question, 'answer': answer} for question, answer in FAQ_QUESTIONS
        ], key='question')

        contact = self.seed_singleton(ContactSection, CONTACT)
        self.seed_items(contact.subjects, [{'name': n} for n in CONTACT_SUBJECTS], key='name')

        self.seed_singleton(CtaSection, CTA)

        footer = self.seed_singleton(Footer, FOOTER)
        for manager, links in [(QuickLink.objects, FOOTER_QUICK_LINKS),
                               (ProgramLink.objects, FOOTER_PROGRAM_LINKS),
                               (LegalLink.objects, FOOTER_LEGAL_LINKS)]:
            self.seed_items(manager, [
                {'label': label, 'link': link, 'footer': footer} for label, link in links
            ], key='label')
        self.seed_items(footer.social_links, [{'platform': p} for p in FOOTER_SOCIAL], key='platform')

        self.stdout.write(self.style.SUCCESS("Seed data loaded successfully."))

    # -----------------------------------------------------------------

    def apply(self, obj, data):
        """
        Normal run: fill only fields that are still empty (e.g. a newly added field),
        so admin edits are never overwritten. --reset: overwrite every seeded field.
        Returns the list of fields that changed.
        """
        changed = []
        for field, value in data.items():
            current = getattr(obj, field)
            if current == value:
                continue
            if self.reset or current in ('', None):
                setattr(obj, field, value)
                changed.append(field)
        if changed:
            obj.save()
        return changed

    def seed_singleton(self, model, data):
        obj, created = model.objects.get_or_create(pk=1, defaults=data)
        if created:
            state = "created"
        else:
            changed = self.apply(obj, data)
            state = f"updated {', '.join(changed)}" if changed else "up to date"
        self.stdout.write(f"  {model._meta.verbose_name}: {state}")
        return obj

    def seed_items(self, manager, rows, key):
        """
        Match each row by `key`. Missing rows are created (in design order);
        existing rows only get empty fields filled (or everything with --reset).
        Rows you added yourself in admin are never touched.
        """
        created = updated = 0
        for order, row in enumerate(rows, start=1):
            data = {**row}
            lookup = {key: data.pop(key)}
            obj = manager.filter(**lookup).first()
            if obj is None:
                manager.create(**lookup, **data, order=order)
                created += 1
            else:
                if self.reset:
                    data['order'] = order
                if self.apply(obj, data):
                    updated += 1
        name = manager.model._meta.verbose_name_plural
        self.stdout.write(f"  {name}: {created} created, {updated} updated, {len(rows)} in design")
