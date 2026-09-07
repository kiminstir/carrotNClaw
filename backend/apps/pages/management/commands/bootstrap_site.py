import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from wagtail.blocks import StreamValue
from wagtail.models import Page, Site

from apps.music.models import MusicSettings
from apps.navigation.models import FooterSettings, HeaderSettings
from apps.pages.models import FlexPage

HOME_BODY = [
    {
        "type": "hero",
        "value": {
            "heading": "Welcome to Carrot&Claw",
            "subheading": "Warm hearth, cold ale and the best stew this side of the mountains.",
            "background": None,
            "cta": {"label": "See the menu", "page": None, "url": "/menu/"},
        },
    },
    {
        "type": "rich_text",
        "value": "<p>Replace this text in the admin. Every page is built from blocks.</p>",
    },
]

CHILD_PAGES = [
    (
        "About",
        "about",
        [{"type": "rich_text", "value": "<p>The story of the tavern goes here.</p>"}],
    ),
    (
        "Menu",
        "menu",
        [
            {
                "type": "card_grid",
                "value": {
                    "columns": "3",
                    "cards": [
                        {
                            "image": None,
                            "title": "Carrot stew",
                            "subtitle": "House special",
                            "text": "Slow-cooked with root vegetables.",
                            "price": "4 silver",
                            "link": {"label": "", "page": None, "url": ""},
                        }
                    ],
                },
            }
        ],
    ),
    (
        "Gallery",
        "gallery",
        [{"type": "rich_text", "value": "<p>Add an image slider block here.</p>"}],
    ),
    (
        "Staff",
        "staff",
        [
            {
                "type": "card_grid",
                "value": {
                    "columns": "3",
                    "cards": [
                        {
                            "image": None,
                            "title": "The Innkeeper",
                            "subtitle": "Owner",
                            "text": "Knows every regular by name.",
                            "price": "",
                            "link": {"label": "", "page": None, "url": ""},
                        }
                    ],
                },
            }
        ],
    ),
]


def stream(field, raw):
    return StreamValue(field.field.stream_block, raw, is_lazy=True)


class Command(BaseCommand):
    help = "Create the initial site tree, settings and superuser. Safe to run repeatedly."

    def handle(self, *args, **options):
        self.ensure_superuser()
        home = self.ensure_home()
        children = {
            slug: self.ensure_child(home, title, slug, body) for title, slug, body in CHILD_PAGES
        }
        self.ensure_settings(home, children)
        self.stdout.write(self.style.SUCCESS("Site bootstrap complete."))

    def ensure_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not (username and password):
            self.stdout.write("DJANGO_SUPERUSER_* not set; skipping superuser.")
            return
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            return
        user_model.objects.create_superuser(
            username=username, email=os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password=password
        )
        self.stdout.write(f"Created superuser {username}.")

    def ensure_home(self):
        try:
            root = Page.get_first_root_node()
        except AttributeError:
            root = Page.objects.get(depth=1)
        home = FlexPage.objects.child_of(root).filter(slug="home").first()
        if home is None:
            # Wagtail's initial migration creates a plain Page at slug "home" (the
            # default "Welcome to your new Wagtail site!" page). It must be moved
            # out of the way before we can create our own page at that slug; it
            # can't simply be deleted yet because Site.root_page is on_delete=CASCADE
            # and (on a fresh install) the default Site still points at it.
            old_default = Page.objects.child_of(root).filter(slug="home").first()
            if old_default is not None and old_default.specific_class is Page:
                old_default.slug = "replaced-by-bootstrap-site"
                old_default.save()

            home = FlexPage(
                title="Carrot&Claw", slug="home", intro="An in-game tavern with a real welcome."
            )
            home.body = stream(FlexPage.body, HOME_BODY)
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write("Created home page.")

        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(hostname="localhost", root_page=home, is_default_site=True)
        elif site.root_page_id != home.pk:
            old_root = site.root_page
            site.root_page = home
            site.save()
            if old_root.specific_class is Page:  # Wagtail's default "Welcome" page
                old_root.delete()
        return home

    def ensure_child(self, home, title, slug, body):
        page = FlexPage.objects.child_of(home).filter(slug=slug).first()
        if page is None:
            page = FlexPage(title=title, slug=slug)
            page.body = stream(FlexPage.body, body)
            home.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(f"Created page {title}.")
        return page

    def ensure_settings(self, home, children):
        header = HeaderSettings.load()
        if len(header.menu) == 0:
            links = [("Home", home)] + [(p.title, p) for p in children.values()]
            header.menu = stream(
                HeaderSettings.menu,
                [
                    {"type": "link", "value": {"label": label, "page": page.pk, "url": ""}}
                    for label, page in links
                ],
            )
            header.save()

        footer = FooterSettings.load()
        if not footer.copyright:
            footer.text = "<p>Open every evening. Find us by the old oak at the crossroads.</p>"
            footer.copyright = "© Carrot&Claw"
            footer.save()

        MusicSettings.load()
