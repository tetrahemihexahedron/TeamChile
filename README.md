# NM Food Connect — TeamChile
**Desert Dev Lab 2026 · NM Tech Talks · April 18-19, 2026**

A two-sided marketplace connecting New Mexico's USDA-verified 
Approved Supplier Program (ASP) farms to institutional buyers 
— K-12 schools, preschools, and senior centers — with 
built-in PED Farm to School grant compliance.

---

## The Problem
22 of 33 New Mexico counties have institutional buyers ready 
to purchase local food but face barriers connecting to 
ASP-approved local farms. NM Food Connect closes that gap.

**Verified data:**
- 131 ASP-verified NM farms · 150 institutional buyers
- 7 counties have buyers but zero local ASP farms
- 23.3% NM child food insecurity — 4th highest nationally
- 75% of NM students qualify for free/reduced lunch
- PED Farm to School grant requires 36-hr fresh delivery window

---

## Tech Stack
- **Backend:** Django 6.0.4
- **Database:** Supabase (Postgres 17) — hosted, no local DB needed
- **Package manager:** uv
- **Python:** 3.14.3

---

## Quick Start

### 1. Clone the repo
git clone https://github.com/tetrahemihexahedron/TeamChile.git
cd TeamChile

### 2. Create your .env file
Copy template.env to .env and fill in the Supabase credentials:

cp template.env .env

Then edit .env:
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<get from team>
DB_HOST=<get from team>

⚠️ Never commit .env — it is gitignored.

### 3. Install dependencies
uv sync

### 4. Start the server
uv run python chile/manage.py runserver

### 5. Open in browser
http://localhost:8000

---

## ⚠️ Important — Do NOT run migrations
The database schema already exists in Supabase.
Never run:
  python manage.py migrate
  python manage.py makemigrations

---

## Screens & URLs

| Screen | URL |
|---|---|
| Home / Landing | http://localhost:8000 |
| Market View | http://localhost:8000/listings/ |
| Request Submission | http://localhost:8000/listings/<id>/request/ |
| Create Listing | http://localhost:8000/listings/create/ |
| Farm Dashboard | http://localhost:8000/farm/dashboard/ |
| Buyer Dashboard | http://localhost:8000/buyer/dashboard/ |
| Impact / Data | http://localhost:8000/data/ |
| Django Admin | http://localhost:8000/admin/ |

---

## White Glove Intake
Farmers can call or text (505) NM-GROW and NM Food Connect 
staff will create listings on their behalf via Django admin.
Listings are tagged with source: phone_assisted, 
email_manifest, text_manifest, or self_service.

---

## Figma Mockups
All 7 screen designs are in:
DDL2026 — NM Food Connect Mock-Ups/

---

## Data Sources
- NM Grown Approved Supplier Program FY2026
- NM Public Education Department Farm to School FAQ
- USDA 2023 Food Security Report
- NM Legislative Council 2020 Census
- NM Voices for Children

---

## Team
TeamChile · Desert Dev Lab 2026
