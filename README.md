# 🦇 Skytattoo.art

A gothic, dark-themed **tattoo studio website** built with Django. Each artist has
their own mini-site profile, the studio portfolio is interactive with animated
tag filtering, and the whole thing is managed from a customised admin dashboard.

## ✨ Features

- **Homepage** — animated GSAP hero, featured portfolio grid, artist teaser, CTAs.
- **Artists** — list + per-artist profile page (bio, specialties, filterable 5-per-row portfolio, YouTube/Vimeo reels, and an **Instagram/TikTok social-proof feed**).
- **Social feed widget** — each artist can paste public Instagram post/reel or TikTok video URLs in the dashboard; the platform is auto-detected and the posts embed live below their portfolio (no API keys — uses the official embed scripts). Add real profile URLs for "Follow" buttons.
- **Studio Portfolio** — masonry layout with animated multi-tag filtering (Isotope.js) by style, colour and size.
- **About** — studio story, values, team.
- **Contact** — Django form (honeypot + optional reCAPTCHA), Google Maps embed, social links.
- **Booking** — appointment request form, pre-fills the chosen artist.
- **Custom dashboard** (`/dashboard/`) — a beautiful gothic control panel that manages **every section of the site**: hero + homepage sections (with show/hide toggles), About story + value cards, branding, SEO, contact info, social links, plus full CRUD for artists (with inline reels), portfolio, styles, bookings and messages. Stat overview with recent activity.
- **Django admin** (`/admin/`) — kept as a power-user fallback with full CRUD too.

## 🎨 Design

Gothic dark theme — `#000000` / `#1a1a1a` / deep red `#8B0000` / gold `#FFD700`,
blackletter (Pirata One) + Cinzel display + Inter body. Animations via GSAP +
ScrollTrigger; portfolio filtering via Isotope.js.

## 🛠 Tech stack

| Layer     | Choice                                        |
|-----------|-----------------------------------------------|
| Backend   | Django 5.2 (Python 3.11+)                     |
| Database  | SQLite (dev) · PostgreSQL/MySQL (prod)        |
| Frontend  | TailwindCSS (Play CDN), GSAP, Isotope.js      |
| Static    | WhiteNoise                                     |

## 🚀 Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (optional) configure environment
cp .env.example .env

# 3. Migrate the database
python manage.py migrate

# 4. Seed gothic demo content + generated placeholder art
python manage.py seed_demo

# 5. Create an admin user
python manage.py createsuperuser

# 6. Run
python manage.py runserver
```

Then open:

- Site — http://127.0.0.1:8000/
- **Dashboard — http://127.0.0.1:8000/dashboard/** (custom gothic control panel)
- Django admin — http://127.0.0.1:8000/admin/

Demo login: **`admin`** / **`skytattoo123`** (created by `createsuperuser` above; the seed assumes a staff user exists).

## 📁 Project structure

```
Skytattoo.art/
├── skytattoo/          # project settings & root URLs
├── core/               # homepage, about, contact, booking, SiteSetting, StudioValue, seed_demo
├── artists/            # Artist + Reel models, list & profile pages
├── portfolio/          # TattooStyle + PortfolioItem, gallery with filtering
├── dashboard/          # custom gothic control panel (views, forms, urls)
├── templates/          # gothic templates (base + per-app + dashboard/)
├── static/             # gothic.css, main.js
└── media/              # user uploads (generated placeholders after seeding)
```

## 🌐 Production notes

- Set `DJANGO_DEBUG=False` and a real `DJANGO_SECRET_KEY` / `DJANGO_ALLOWED_HOSTS`.
- Point `DB_ENGINE` etc. at PostgreSQL or MySQL.
- Run `python manage.py collectstatic`; WhiteNoise serves the hashed assets.
- Swap the Tailwind Play CDN for a compiled Tailwind build for best performance.
- Configure SMTP + reCAPTCHA keys for the contact/booking forms.
