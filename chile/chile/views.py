from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import connection
from django.http import Http404

from .models import (
    Farm, Buyer, Listing, Request, NMCounty,
    CropCategory, QuantityUnit, ListingStatus, RequestStatus,
)


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# S1 — Landing
# ---------------------------------------------------------------------------

def landing(request):
    farm_count = Farm.objects.filter(nm_grown_asp_approved=True, active=True).count()
    buyer_count = Buyer.objects.filter(active=True).count()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT b.county) AS counties_with_buyers
            FROM buyers b
            WHERE b.active = TRUE AND b.county IS NOT NULL
        """)
        counties_with_buyers = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT count(*) FROM vw_county_supply_gap
            WHERE asp_farms_in_county = 0 AND buyers_in_county > 0
        """)
        underserved_counties = cursor.fetchone()[0] or 0

    return render(request, "landing.html", {
        "farm_count": farm_count,
        "buyer_count": buyer_count,
        "underserved_counties": underserved_counties,
        "total_counties": 33,
    })


# ---------------------------------------------------------------------------
# S2 — Market View
# ---------------------------------------------------------------------------

def market_view(request):
    now = timezone.now()
    today = now.date()

    category = request.GET.get("category", "")
    county = request.GET.get("county", "")
    vendor_type = request.GET.get("vendor_type", "")
    ped_filter = request.GET.get("ped", "")
    search = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "ped_hours")

    qs = Listing.objects.filter(
        status__in=[ListingStatus.ACTIVE, ListingStatus.EXPIRING],
        availability_end__gte=today,
    ).select_related("farm")

    if category:
        qs = qs.filter(category=category)
    if county:
        qs = qs.filter(farm__county=county)
    if vendor_type:
        qs = qs.filter(farm__vendor_type=vendor_type)
    if search:
        qs = qs.filter(crop_name__icontains=search) | qs.filter(farm__name__icontains=search)
    if ped_filter == "grant_eligible":
        qs = qs.filter(ped_eligible=True)
    elif ped_filter == "always_eligible":
        qs = qs.filter(ped_eligible_items=True)

    listings = list(qs)

    # Annotate PED hours remaining in Python
    for listing in listings:
        if listing.harvest_timestamp and not listing.ped_eligible_items:
            deadline = listing.harvest_timestamp + timezone.timedelta(hours=36)
            remaining = deadline - now
            listing.ped_hours_remaining = max(0, remaining.total_seconds() / 3600)
            listing.ped_window_expired = remaining.total_seconds() <= 0
        elif listing.ped_eligible_items:
            listing.ped_hours_remaining = None
            listing.ped_window_expired = False
        else:
            listing.ped_hours_remaining = None
            listing.ped_window_expired = None

    if sort == "ped_hours":
        listings.sort(key=lambda l: (
            l.ped_hours_remaining is None,
            l.ped_hours_remaining or 0
        ))
    elif sort == "price_asc":
        listings.sort(key=lambda l: l.price_per_unit)
    elif sort == "price_desc":
        listings.sort(key=lambda l: l.price_per_unit, reverse=True)

    counties = Farm.objects.filter(active=True).values_list("county", flat=True).distinct().order_by("county")

    return render(request, "market_view.html", {
        "listings": listings,
        "listing_count": len(listings),
        "categories": CropCategory.choices,
        "counties": [c for c in counties if c],
        "selected_category": category,
        "selected_county": county,
        "selected_vendor_type": vendor_type,
        "selected_ped": ped_filter,
        "search": search,
        "sort": sort,
    })


# ---------------------------------------------------------------------------
# S3 — Request Submission
# ---------------------------------------------------------------------------

def request_submission(request, listing_id):
    listing = get_object_or_404(
        Listing.objects.select_related("farm", "crop"),
        id=listing_id,
        status__in=[ListingStatus.ACTIVE, ListingStatus.EXPIRING],
    )
    now = timezone.now()

    if listing.harvest_timestamp and not listing.ped_eligible_items:
        deadline = listing.harvest_timestamp + timezone.timedelta(hours=36)
        ped_hours_remaining = max(0, (deadline - now).total_seconds() / 3600)
        ped_window_expired = (deadline - now).total_seconds() <= 0
    elif listing.ped_eligible_items:
        ped_hours_remaining = None
        ped_window_expired = False
    else:
        ped_hours_remaining = None
        ped_window_expired = None

    pending_requests = Request.objects.filter(
        listing=listing,
        status__in=[RequestStatus.PENDING, RequestStatus.ACCEPTED],
    ).select_related("buyer")

    committed_qty = sum(r.quantity_requested for r in pending_requests)
    remaining_qty = listing.quantity_available - committed_qty

    # Use first active buyer as placeholder until auth is wired
    buyer = Buyer.objects.filter(active=True).first()

    errors = {}
    if request.method == "POST":
        qty_str = request.POST.get("quantity_requested", "").strip()
        delivery_date = request.POST.get("delivery_date", "").strip()
        delivery_time = request.POST.get("delivery_time", "").strip()
        delivery_location = request.POST.get("delivery_location", "").strip()
        message = request.POST.get("message", "").strip()
        ped_confirm = request.POST.get("ped_confirm")

        try:
            qty = float(qty_str)
        except ValueError:
            qty = None
            errors["quantity"] = "Enter a valid number."

        if qty is not None:
            if listing.min_order_qty and qty < float(listing.min_order_qty):
                errors["quantity"] = f"Minimum order is {listing.min_order_qty} {listing.quantity_unit}."
            if qty > float(remaining_qty):
                errors["quantity"] = f"Only {remaining_qty} {listing.quantity_unit} remaining."

        if not delivery_date:
            errors["delivery_date"] = "Delivery date is required."

        if not errors and buyer:
            requested_delivery = None
            if delivery_date and delivery_time:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(f"{delivery_date} {delivery_time}", "%Y-%m-%d %H:%M")
                    requested_delivery = timezone.make_aware(dt)
                except ValueError:
                    pass

            Request.objects.create(
                listing=listing,
                buyer=buyer,
                quantity_requested=qty,
                message=message or None,
                requested_delivery=requested_delivery,
                status=RequestStatus.PENDING,
            )
            return redirect("buyer_dashboard")

    return render(request, "request_submission.html", {
        "listing": listing,
        "ped_hours_remaining": ped_hours_remaining,
        "ped_window_expired": ped_window_expired,
        "pending_requests": pending_requests,
        "remaining_qty": remaining_qty,
        "buyer": buyer,
        "errors": errors,
        "post": request.POST if request.method == "POST" else {},
        "harvest_ago_hours": (
            (now - listing.harvest_timestamp).total_seconds() / 3600
            if listing.harvest_timestamp else None
        ),
    })


# ---------------------------------------------------------------------------
# S4 — Create Listing
# ---------------------------------------------------------------------------

def create_listing(request):
    # Use first active farm as placeholder until auth is wired
    farm = Farm.objects.filter(active=True, nm_grown_asp_approved=True).first()
    errors = {}
    preview = None

    if request.method == "POST":
        crop_name = request.POST.get("crop_name", "").strip()
        variety = request.POST.get("variety", "").strip()
        category = request.POST.get("category", "").strip()
        qty_str = request.POST.get("quantity_available", "").strip()
        unit = request.POST.get("quantity_unit", "lbs")
        price_str = request.POST.get("price_per_unit", "").strip()
        min_qty_str = request.POST.get("min_order_qty", "").strip()
        harvest_date = request.POST.get("harvest_date", "").strip()
        harvest_time = request.POST.get("harvest_time", "").strip()
        avail_from = request.POST.get("availability_start", "").strip()
        avail_until = request.POST.get("availability_end", "").strip()
        certifications_raw = request.POST.getlist("certifications")
        always_eligible = bool(request.POST.get("ped_eligible_items"))
        notes = request.POST.get("notes", "").strip()
        action = request.POST.get("action", "publish")

        if not crop_name:
            errors["crop_name"] = "Crop name is required."
        if not category:
            errors["category"] = "Category is required."

        try:
            qty = float(qty_str)
        except ValueError:
            qty = None
            errors["quantity_available"] = "Enter a valid quantity."

        try:
            price = float(price_str)
        except ValueError:
            price = None
            errors["price_per_unit"] = "Enter a valid price."

        min_qty = None
        if min_qty_str:
            try:
                min_qty = float(min_qty_str)
            except ValueError:
                errors["min_order_qty"] = "Enter a valid minimum quantity."

        harvest_ts = None
        if harvest_date and harvest_time:
            try:
                from datetime import datetime
                dt = datetime.strptime(f"{harvest_date} {harvest_time}", "%Y-%m-%d %H:%M")
                harvest_ts = timezone.make_aware(dt)
            except ValueError:
                errors["harvest_date"] = "Invalid harvest date/time."
        elif harvest_date:
            errors["harvest_time"] = "Harvest time is required for PED compliance."

        if not avail_from:
            errors["availability_start"] = "Available from date is required."
        if not avail_until:
            errors["availability_end"] = "Available until date is required."

        certifications = [c for c in certifications_raw if c] or None

        if action == "preview" or not errors:
            preview = {
                "crop_name": crop_name,
                "variety": variety,
                "farm": farm,
                "qty": qty,
                "unit": unit,
                "price": price,
                "harvest_ts": harvest_ts,
                "certifications": certifications,
                "always_eligible": always_eligible,
                "ped_hours_remaining": (
                    36 - (timezone.now() - harvest_ts).total_seconds() / 3600
                    if harvest_ts else None
                ),
            }

        if action == "publish" and not errors and farm:
            from datetime import date
            try:
                avail_start_date = date.fromisoformat(avail_from)
                avail_end_date = date.fromisoformat(avail_until)
            except ValueError:
                avail_start_date = timezone.now().date()
                avail_end_date = timezone.now().date()

            Listing.objects.create(
                farm=farm,
                crop_name=crop_name,
                variety=variety or None,
                category=category,
                quantity_available=qty,
                quantity_unit=unit,
                min_order_qty=min_qty,
                price_per_unit=price,
                harvest_timestamp=harvest_ts,
                availability_start=avail_start_date,
                availability_end=avail_end_date,
                ped_eligible=bool(harvest_ts),
                ped_eligible_items=always_eligible,
                certifications=certifications,
                notes=notes or None,
                status=ListingStatus.ACTIVE,
                source="self_service",
            )
            return redirect("farm_dashboard")

    return render(request, "create_listing.html", {
        "farm": farm,
        "categories": CropCategory.choices,
        "units": QuantityUnit.choices,
        "certifications": ['USDA Organic', 'GAP Certified', 'Spray-free', 'Conventional', 'Other'],
        "errors": errors,
        "preview": preview,
        "post": request.POST if request.method == "POST" else {},
    })


# ---------------------------------------------------------------------------
# S5 — Farm Dashboard
# ---------------------------------------------------------------------------

def farm_dashboard(request):
    farm = Farm.objects.filter(active=True, nm_grown_asp_approved=True).first()
    if not farm:
        raise Http404

    today = timezone.now().date()
    listings = Listing.objects.filter(farm=farm).order_by("availability_end")

    active_listings = [l for l in listings if l.status in (ListingStatus.ACTIVE, ListingStatus.EXPIRING)]
    expiring_soon = [l for l in active_listings if l.availability_end <= today + timezone.timedelta(days=7)]

    pending_requests = Request.objects.filter(
        listing__farm=farm,
        status=RequestStatus.PENDING,
    ).select_related("buyer", "listing").order_by("-created_at")

    fulfilled_count = Request.objects.filter(
        listing__farm=farm,
        status=RequestStatus.FULFILLED,
    ).count()

    accepted_count = Request.objects.filter(
        listing__farm=farm,
        status=RequestStatus.ACCEPTED,
    ).count()

    total_responded = Request.objects.filter(
        listing__farm=farm,
        status__in=[RequestStatus.ACCEPTED, RequestStatus.DECLINED, RequestStatus.FULFILLED],
    ).count()
    total_requests = Request.objects.filter(listing__farm=farm).count()
    match_rate = round(accepted_count / total_responded * 100) if total_responded else 0

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(r.quantity_requested * l.price_per_unit), 0)
            FROM requests r
            JOIN listings l ON r.listing_id = l.id
            WHERE l.farm_id = %s
              AND r.status IN ('Accepted', 'Fulfilled')
        """, [str(farm.id)])
        revenue_est = cursor.fetchone()[0] or 0

    # Annotate listings with pending request counts
    for listing in listings:
        listing.pending_count = sum(
            1 for r in pending_requests if r.listing_id == listing.id
        )

    return render(request, "farm_dashboard.html", {
        "farm": farm,
        "listings": listings,
        "active_count": len(active_listings),
        "expiring_count": len(expiring_soon),
        "pending_requests": pending_requests,
        "pending_count": len(pending_requests),
        "fulfilled_count": fulfilled_count,
        "match_rate": match_rate,
        "revenue_est": revenue_est,
        "today": today,
    })


def respond_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    action = request.POST.get("action")
    if action == "accept":
        req.status = RequestStatus.ACCEPTED
        req.responded_at = timezone.now()
        req.save()
    elif action == "decline":
        req.status = RequestStatus.DECLINED
        req.responded_at = timezone.now()
        req.save()
    return redirect("farm_dashboard")


# ---------------------------------------------------------------------------
# S6 — Buyer Dashboard
# ---------------------------------------------------------------------------

def buyer_dashboard(request):
    buyer = Buyer.objects.filter(active=True).first()
    if not buyer:
        raise Http404

    requests = Request.objects.filter(buyer=buyer).select_related(
        "listing", "listing__farm"
    ).order_by("-created_at")

    active_requests = [r for r in requests if r.status in (RequestStatus.PENDING, RequestStatus.ACCEPTED)]
    accepted_count = sum(1 for r in requests if r.status == RequestStatus.ACCEPTED)
    fulfilled_count = sum(1 for r in requests if r.status == RequestStatus.FULFILLED)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(r.quantity_requested * l.price_per_unit), 0)
            FROM requests r
            JOIN listings l ON r.listing_id = l.id
            WHERE r.buyer_id = %s
              AND r.status IN ('Accepted', 'Fulfilled')
        """, [str(buyer.id)])
        spent_est = cursor.fetchone()[0] or 0

    ped_eligible_count = sum(1 for r in requests if r.listing.ped_eligible or r.listing.ped_eligible_items)
    ped_pct = round(ped_eligible_count / len(requests) * 100) if requests else 0

    now = timezone.now()
    recommended = Listing.objects.filter(
        status=ListingStatus.ACTIVE,
        availability_end__gte=now.date(),
    ).exclude(
        id__in=[r.listing_id for r in requests]
    ).select_related("farm").order_by("availability_end")[:3]

    for listing in recommended:
        if listing.harvest_timestamp and not listing.ped_eligible_items:
            deadline = listing.harvest_timestamp + timezone.timedelta(hours=36)
            listing.ped_hours_remaining = max(0, (deadline - now).total_seconds() / 3600)
        else:
            listing.ped_hours_remaining = None

    return render(request, "buyer_dashboard.html", {
        "buyer": buyer,
        "requests": requests,
        "active_count": len(active_requests),
        "accepted_count": accepted_count,
        "fulfilled_count": fulfilled_count,
        "spent_est": spent_est,
        "ped_pct": ped_pct,
        "recommended": recommended,
    })


# ---------------------------------------------------------------------------
# S7 — Data / Impact Page
# ---------------------------------------------------------------------------

def data_page(request):
    farm_count = Farm.objects.filter(nm_grown_asp_approved=True, active=True).count()
    buyer_count = Buyer.objects.filter(active=True).count()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                n.county_name,
                n.region,
                n.food_insecurity_rate_pct,
                n.child_food_insecurity_rate_pct,
                COUNT(DISTINCT f.id) AS asp_farms,
                COUNT(DISTINCT b.id) AS buyers,
                CASE
                    WHEN COUNT(DISTINCT f.id) = 0 THEN 'No local farms'
                    WHEN COUNT(DISTINCT b.id) > COUNT(DISTINCT f.id) * 2 THEN 'Underserved'
                    WHEN COUNT(DISTINCT b.id) > COUNT(DISTINCT f.id) THEN 'Partially covered'
                    ELSE 'Well covered'
                END AS coverage_status
            FROM nm_counties n
            LEFT JOIN farms f ON f.county = n.county_name AND f.nm_grown_asp_approved = TRUE AND f.active = TRUE
            LEFT JOIN buyers b ON b.county = n.county_name AND b.active = TRUE
            GROUP BY n.county_name, n.region, n.food_insecurity_rate_pct, n.child_food_insecurity_rate_pct
            ORDER BY n.food_insecurity_rate_pct DESC NULLS LAST
        """)
        counties = dictfetchall(cursor)

        cursor.execute("""
            SELECT COUNT(DISTINCT b.county)
            FROM buyers b
            WHERE b.active = TRUE
              AND b.county IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM farms f
                WHERE f.active = TRUE
                  AND f.nm_grown_asp_approved = TRUE
                  AND f.county = b.county
              )
        """)
        underserved_count = cursor.fetchone()[0] or 0

    no_farm_counties = [c for c in counties if c["asp_farms"] == 0 and c["buyers"] > 0]

    return render(request, "data_page.html", {
        "farm_count": farm_count,
        "buyer_count": buyer_count,
        "underserved_count": underserved_count,
        "total_counties": 33,
        "counties": counties,
        "no_farm_counties": no_farm_counties,
    })
