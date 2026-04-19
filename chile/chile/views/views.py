from django.shortcuts import render
from django.utils import timezone

from chile.models import Listing


def test(request):
    today = timezone.localdate()
    listings = (
        Listing.objects.filter(
            availability_start__gt=today,
            availability_end__gt=today,
        )
        .only("crop_name", "quantity_available", "quantity_unit", "availability_start")
        .order_by("availability_start", "availability_end", "crop_name")
    )

    return render(request, "test.html", {"listings": listings, "today": today})
