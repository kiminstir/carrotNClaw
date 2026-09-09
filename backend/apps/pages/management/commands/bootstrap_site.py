import copy
import os
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.blocks import StreamValue
from wagtail.models import Page, Site

from apps.music.models import MusicSettings
from apps.navigation.models import FooterSettings, HeaderSettings
from apps.pages.models import FlexPage


def rich_text(html):
    return {
        "type": "rich_text",
        "value": {
            "text": html,
            "color": "default",
            "size": "md",
            "line_height": "normal",
            "align": "left",
        },
    }


HOME_BODY = [
    {
        "type": "hero",
        "value": {
            "heading": "Welcome to Carrot&Claw",
            "subheading": "Warm hearth, cold ale and the best stew this side of the mountains.",
            "background": None,
            "cta": {"label": "See the menu", "page": None, "url": ""},
        },
    },
    rich_text("<p>Replace this text in the admin. Every page is built from blocks.</p>"),
]

CHILD_PAGES = [
    (
        "About",
        "about",
        [rich_text("<p>The story of the tavern goes here.</p>")],
    ),
    (
        "Menu",
        "menu",
        [
            {
                "type": "card_grid",
                "value": {
                    "columns": "3",
                    "style": "artwork",
                    "cards": [
                        {
                            "image": None,
                            "title": "Carrot stew",
                            "subtitle": "House special",
                            "text": "Slow-cooked with root vegetables.",
                            "price": "4 silver",
                            "link": {"label": "", "page": None, "url": ""},
                            "description": "",
                            "detail_images": [],
                        }
                    ],
                },
            }
        ],
    ),
    (
        "Gallery",
        "gallery",
        [rich_text("<p>Add an image slider block here.</p>")],
    ),
    (
        "Staff",
        "staff",
        [
            {
                "type": "card_grid",
                "value": {
                    "columns": "3",
                    "style": "portrait",
                    "cards": [
                        {
                            "image": None,
                            "title": "The Innkeeper",
                            "subtitle": "Owner",
                            "text": "Knows every regular by name.",
                            "price": "",
                            "link": {"label": "", "page": None, "url": ""},
                            "description": "",
                            "detail_images": [],
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

    @transaction.atomic
    def handle(self, *args, **options):
        self.ensure_superuser()
        home = self.ensure_home()
        children = {
            slug: self.ensure_child(home, title, slug, body) for title, slug, body in CHILD_PAGES
        }
        self.link_hero_cta_to_menu(home, children.get("menu"))
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
        root = Page.get_first_root_node()
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
            site = Site.objects.create(hostname="localhost", root_page=home, is_default_site=True)
        elif site.root_page_id != home.pk:
            old_root = site.root_page
            site.root_page = home
            site.save()
            if old_root.specific_class is Page:  # Wagtail's default "Welcome" page
                old_root.delete()

        if site.hostname == "localhost":
            # Wagtail's initial migration (and the branch above, for a fresh
            # install) both leave the default Site at hostname "localhost".
            # Point it at the real frontend host instead - but only while it
            # is still at that placeholder, so an operator who has since set
            # a real hostname is never overridden by a later bootstrap run.
            parsed = urlparse(settings.FRONTEND_URL)
            default_port = 443 if parsed.scheme == "https" else 80
            site.hostname = parsed.hostname or "localhost"
            site.port = parsed.port or default_port
            site.site_name = "Carrot&Claw"
            site.save()

        # Self-healing: once the Site is (re)pointed at `home`, nothing should
        # reference any other depth-2 page any more. Clean up any leftover
        # plain Page (never a FlexPage) at depth 2 - e.g. a renamed default
        # "Welcome" page left behind by a run that was interrupted before it
        # could be deleted, on an older version of this command, or one
        # recreated by hand.
        for stray in Page.objects.filter(depth=2).exclude(pk=home.pk):
            if stray.specific_class is Page:
                stray.delete()
        return home

    def link_hero_cta_to_menu(self, home, menu):
        if menu is None:
            return
        # Deep-copy: get_prep_value() can hand back the same dicts backing the
        # module-level HOME_BODY constant (for a stream that was never
        # touched), and mutating those in place would corrupt every home
        # page created for the rest of the process's lifetime.
        raw = copy.deepcopy(home.body.get_prep_value())
        if not raw or raw[0].get("type") != "hero":
            return
        cta = raw[0]["value"].get("cta") or {}
        if cta.get("page") or cta.get("url"):
            return  # already set - by an earlier run, or by an editor
        cta["page"] = menu.pk
        raw[0]["value"]["cta"] = cta
        home.body = stream(FlexPage.body, raw)
        home.save_revision().publish()
        self.stdout.write("Linked hero CTA to the Menu page.")

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
