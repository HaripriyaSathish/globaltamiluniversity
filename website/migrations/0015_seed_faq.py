"""
Load the FAQ heading and questions once, when the FAQ section is still empty.
Runs automatically with `migrate` on deploy (no shell needed). Later edits in
admin are never touched, and deleted questions are not added back.
"""
from django.db import migrations

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


def seed_faq(apps, schema_editor):
    FaqSection = apps.get_model('website', 'FaqSection')
    FaqItem = apps.get_model('website', 'FaqItem')

    section, _ = FaqSection.objects.get_or_create(
        pk=1, defaults={'eyebrow': "FAQ", 'title': "Frequently Asked Questions", 'is_active': True})
    if FaqItem.objects.filter(section=section).exists():
        return
    FaqItem.objects.bulk_create([
        FaqItem(section=section, question=q, answer=a, order=i, is_active=True)
        for i, (q, a) in enumerate(FAQ_QUESTIONS, start=1)
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_faqsection_faqitem'),
    ]

    operations = [
        migrations.RunPython(seed_faq, migrations.RunPython.noop),
    ]
