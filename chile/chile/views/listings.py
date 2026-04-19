from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from chile.forms import ListingForm
from chile.models import CropCategory, Farm, QuantityUnit


def create_listing(request, farm_id):
    # TODO: get farm from farm_id
    farm = Farm.objects.first()
    if farm is None:
        raise Http404("Farm not found")

    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.farm = farm

            # TODO: collect this data in the form
            listing.category = CropCategory.VEGETABLES
            listing.quantity_unit = QuantityUnit.LBS
            listing.price_per_unit = Decimal("1")
            today = timezone.localdate()
            listing.availability_start = today
            listing.availability_end = today + timedelta(days=30)
            listing.save()
            messages.success(
                request,
                f"Listing “{listing.crop_name}” was created.",
            )
            # TODO: redirect to farm dashboard
            return redirect(reverse("home"))
    else:
        form = ListingForm()

    return render(
        request,
        "listings/create.html",
        {"farm": farm, "form": form},
    )
