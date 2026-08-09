"""Populate the database with gothic demo content + generated placeholder art.

Run with:  python manage.py seed_demo

Images are generated on the fly with Pillow so the studio looks complete
without any real uploads. Safe to re-run: it clears demo content first.
"""

import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from artists.models import Artist, Reel, SocialPost
from core.models import SiteSetting, StudioValue
from portfolio.models import PortfolioImage, PortfolioItem, TattooStyle

# Gothic palette
INK = (10, 10, 10)
CHAR = (26, 26, 26)
BLOOD = (139, 0, 0)
GOLD = (255, 215, 0)


def _font(size):
    for name in ("seguisb.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _placeholder(text, w=900, h=1100, accent=BLOOD, seed=0):
    """Return a dark, textured placeholder image as a Django ContentFile."""
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), INK)
    draw = ImageDraw.Draw(img)

    # Vertical gradient wash from accent -> ink.
    for y in range(h):
        t = y / h
        r = int(accent[0] * (1 - t) * 0.35 + INK[0] * t)
        g = int(accent[1] * (1 - t) * 0.35 + INK[1] * t)
        b = int(accent[2] * (1 - t) * 0.35 + INK[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Scattered "ink" strokes for texture.
    for _ in range(60):
        x1, y1 = rnd.randint(0, w), rnd.randint(0, h)
        x2, y2 = x1 + rnd.randint(-140, 140), y1 + rnd.randint(-140, 140)
        shade = rnd.randint(20, 60)
        draw.line([(x1, y1), (x2, y2)], fill=(shade, shade, shade), width=rnd.randint(1, 3))

    # Thin gold frame.
    draw.rectangle([18, 18, w - 18, h - 18], outline=GOLD, width=2)

    # Centered label.
    font = _font(int(w / 11))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2 - bbox[1]), text, font=font, fill=GOLD)

    small = _font(int(w / 26))
    tag = "SKYTATTOO.ART"
    tb = draw.textbbox((0, 0), tag, font=small)
    draw.text(((w - (tb[2] - tb[0])) / 2, h - 70), tag, font=small, fill=(150, 150, 150))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Seed the database with gothic demo content and placeholder images."

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing demo content…")
        PortfolioItem.objects.all().delete()
        PortfolioImage.objects.all().delete()
        Reel.objects.all().delete()
        Artist.objects.all().delete()
        TattooStyle.objects.all().delete()

        # ---- Site settings ----
        site = SiteSetting.load()
        site.site_name = "Skytattoo.art"
        site.tagline = "Gothic ink. Timeless art."
        site.about_short = (
            "A Tbilisi tattoo studio devoted to blackwork, realism and the gothic. "
            "We turn ideas into permanent art."
        )
        site.meta_description = (
            "Skytattoo.art — gothic tattoo studio in Tbilisi. Blackwork, realism, "
            "minimal and gothic tattoos by resident artists."
        )
        site.meta_keywords = "tattoo, gothic tattoo, blackwork, realism, Tbilisi tattoo studio"
        site.address = "13 Rustaveli Ave, Tbilisi, Georgia"
        site.phone = "+995 555 13 13 13"
        site.email = "studio@skytattoo.art"
        site.opening_hours = "Mon–Sat · 12:00 – 21:00\nSun · by appointment"
        site.instagram = "https://instagram.com/"
        site.facebook = "https://facebook.com/"
        site.tiktok = "https://tiktok.com/"
        site.youtube = "https://youtube.com/"
        # Homepage content
        site.hero_eyebrow = "Gothic Tattoo Studio · Tbilisi"
        site.hero_title = "Sky"
        site.hero_title_accent = "tattoo"
        site.hero_subtitle = (
            "Gothic ink. Timeless art. — where dark artistry becomes permanent. "
            "Bespoke blackwork, realism and gothic ink by resident masters."
        )
        site.cta_primary_label = "Book Appointment"
        site.cta_secondary_label = "Meet Our Artists"
        site.featured_eyebrow = "Latest Ink"
        site.featured_title = "Featured Portfolio"
        site.artists_eyebrow = "The Coven"
        site.artists_title = "Meet Our Artists"
        site.cta_band_title = "Ready for your next piece?"
        site.cta_band_text = (
            "Book a consultation with one of our artists and let's design something eternal."
        )
        site.cta_band_label = "Book Appointment"
        site.show_portfolio_style_filters = True
        site.show_portfolio_color_filters = False
        site.show_portfolio_size_filters = False
        site.portfolio_cards_square = True
        site.about_story = (
            "Skytattoo.art is a gothic tattoo studio where darkness and craft meet skin. "
            "Founded in 2016 on a love of blackwork, fine-line realism and the macabre, our "
            "artists treat every appointment as a collaboration — turning ideas into permanent "
            "art that outlives trends.\n\n"
            "The studio is a private, sterile space in the heart of Tbilisi, built for focus, "
            "comfort and detail."
        )
        site.save()

        # About page value cards
        StudioValue.objects.all().delete()
        for i, (t, txt) in enumerate([
            ("Bespoke Design", "Every piece is drawn from scratch for you — no flash repeats, no shortcuts."),
            ("Sterile & Safe", "Single-use needles, hospital-grade sterilisation and a spotless private studio."),
            ("Dark Craft", "Blackwork, realism and gothic linework are our obsession, honed over years."),
        ]):
            StudioValue.objects.create(title=t, text=txt, order=i)

        # ---- Styles ----
        style_defs = [
            ("Blackwork", "#8B0000"),
            ("Realism", "#FFD700"),
            ("Minimal", "#9ca3af"),
            ("Gothic", "#6d28d9"),
            ("Dotwork", "#0ea5e9"),
        ]
        styles = {}
        for i, (name, color) in enumerate(style_defs):
            styles[name] = TattooStyle.objects.create(name=name, color=color, order=i)
        self.stdout.write(f"Created {len(styles)} styles.")

        # ---- Artists ----
        artist_defs = [
            ("Mara Voss", "Founder · Blackwork", ["Blackwork", "Gothic"],
             "Mara founded Skytattoo.art in 2016 after a decade tattooing across Berlin and Prague. "
             "Her heavy blackwork and ornamental gothic pieces are the studio's signature."),
            ("Damien Cross", "Resident · Realism", ["Realism", "Dotwork"],
             "Damien specialises in black-and-grey realism — portraits, statues and religious "
             "iconography rendered with obsessive detail."),
            ("Ilse Kroft", "Resident · Fine Line", ["Minimal", "Dotwork"],
             "Ilse's minimal fine-line and dotwork balance the studio's darker leanings with "
             "delicate, precise compositions."),
            ("Rook Halloran", "Guest · Gothic", ["Gothic", "Blackwork"],
             "A recurring guest artist, Rook brings neo-gothic lettering and dark surrealism "
             "from his studio in Edinburgh."),
        ]
        artists = []
        for i, (name, role, style_names, bio) in enumerate(artist_defs):
            a = Artist(
                name=name,
                role=role,
                tagline=bio.split(".")[0] + ".",
                bio=bio,
                instagram="https://instagram.com/",
                order=i,
            )
            a.avatar.save(
                f"{a.name.lower().replace(' ', '_')}_avatar.jpg",
                _placeholder(name.split()[0], 700, 700, seed=i * 7),
                save=False,
            )
            a.cover_image.save(
                f"{a.name.lower().replace(' ', '_')}_cover.jpg",
                _placeholder(name, 1600, 600, accent=CHAR, seed=i * 11),
                save=False,
            )
            a.save()
            a.styles.set([styles[s] for s in style_names])
            artists.append(a)
        self.stdout.write(f"Created {len(artists)} artists.")

        # ---- Portfolio items ----
        titles = [
            "Raven Requiem", "Cathedral Sleeve", "Momento Mori", "Ornamental Veil",
            "Saint of Ash", "Black Rose", "Serpent Crown", "Fallen Seraph",
            "Gilded Skull", "Nocturne", "Ivory Reliquary", "Thorn Mandala",
            "Hollow Saint", "Requiem Hand", "Dusk Portrait", "Sigil of Dust",
        ]
        colors = [c[0] for c in PortfolioItem.Color.choices]
        sizes = [s[0] for s in PortfolioItem.Size.choices]
        style_list = list(styles.values())

        created = 0
        for i, title in enumerate(titles):
            artist = artists[i % len(artists)]
            item = PortfolioItem(
                title=title,
                artist=artist,
                color=random.choice(colors),
                size=random.choice(sizes),
                is_featured=i < 8,
                order=i,
                description="Custom freehand piece — black & grey with fine detailing.",
            )
            accent = BLOOD if i % 2 else GOLD
            item.image.save(
                f"work_{i}.jpg",
                _placeholder(title.split()[0], 900, 1100, accent=accent, seed=i * 13),
                save=False,
            )
            item.save()
            chosen = random.sample(style_list, k=random.randint(1, 2))
            # Bias each artist's work toward their own styles.
            chosen = list({*chosen, *list(artist.styles.all())[:1]})
            item.styles.set(chosen)
            for j in range(3):
                gallery = PortfolioImage(item=item, caption=f"{title} detail {j + 1}", order=j)
                gallery.image.save(
                    f"work_{i}_detail_{j + 1}.jpg",
                    _placeholder(f"{title.split()[0]} {j + 1}", 900, 1100, accent=accent, seed=i * 31 + j),
                    save=False,
                )
                gallery.save()
            created += 1
        self.stdout.write(f"Created {created} portfolio items.")

        # ---- Reels (sample public videos) ----
        reel_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
        ]
        for a in artists[:2]:
            for j, url in enumerate(reel_urls):
                Reel.objects.create(
                    artist=a, title=f"{a.name.split()[0]} — Process {j + 1}", video_url=url, order=j
                )

        # ---- Social feed examples (studio replaces with real post URLs) ----
        # These demonstrate the Instagram/TikTok social-proof widget. The URLs
        # are placeholders — real public post/video URLs render as live embeds.
        social_examples = [
            ("https://www.instagram.com/reel/CxampleReel001/", "Fresh linework, healed 2 weeks"),
            ("https://www.tiktok.com/@skytattoo.art/video/7300000000000000001", "Time-lapse: gothic sleeve"),
            ("https://www.instagram.com/p/CxamplePost002/", "Studio session"),
        ]
        for a in artists[:2]:
            for j, (url, cap) in enumerate(social_examples):
                sp = SocialPost(artist=a, url=url, caption=cap, order=j)
                sp.save()  # platform auto-detected in save()

        self.stdout.write(self.style.SUCCESS("Demo content seeded successfully."))
