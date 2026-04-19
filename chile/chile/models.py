import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# Enums (USER-DEFINED types)

class BuyerType(models.TextChoices):
    RESTAURANT = "Restaurant"
    SCHOOL = "School / District"
    GROCERY = "Grocery / Co-op"
    BANK = "Food Bank"
    OTHER = "Other"

class CropCategory(models.TextChoices):
    VEGETABLES = "Vegetables"
    FRUITS = "Fruits"
    GRAINS = "Grains"
    HERBS = "Herbs"
    LEGUMES = "Legumes"
    LIVESTOCK = "Livestock / Dairy"

class QuantityUnit(models.TextChoices):
    LBS = "lbs"
    KG = "kg"
    CASES = "cases"
    FLATS = "flats"
    UNITS = "units"
    EACH = "each"
    BUSHELS = "bushels"

class ListingStatus(models.TextChoices):
    ACTIVE = "Active"
    EXPIRING = "Expiring"
    SOLD_OUT = "Sold Out"
    PAUSED = "Paused"

class RequestStatus(models.TextChoices):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"


class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    type = models.CharField(max_length=50, choices=BuyerType.choices)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    county = models.TextField(null=True, blank=True)
    ped_grant_participant = models.BooleanField(default=False)
    institution_type = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geocoded_at = models.DateTimeField(null=True, blank=True)
    geocode_source = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "buyers"

    def __str__(self):
        return str(self.name)


class Crop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    category = models.CharField(max_length=50, choices=CropCategory.choices)
    season = ArrayField(models.TextField(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "crops"

    def __str__(self):
        return str(self.name)


class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    owner_name = models.TextField()
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    county = models.TextField(null=True, blank=True)
    region = models.TextField(null=True, blank=True)
    certifications = ArrayField(models.TextField(), null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    nm_grown_asp_approved = models.BooleanField(default=False)
    asp_vendor_id = models.TextField(null=True, blank=True)
    asp_approved_since = models.DateField(null=True, blank=True)
    asp_counties_served = ArrayField(models.TextField(), null=True, blank=True)
    zip = models.TextField(null=True, blank=True)
    products_offered = ArrayField(models.TextField(), null=True, blank=True)
    vendor_type = models.TextField(null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geocoded_at = models.DateTimeField(null=True, blank=True)
    geocode_source = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "farms"

    def __str__(self):
        return str(self.name)


class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="listings")
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    crop_name = models.TextField()
    variety = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CropCategory.choices)
    quantity_available = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_unit = models.CharField(max_length=50, choices=QuantityUnit.choices)
    min_order_qty = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    certifications = ArrayField(models.TextField(), null=True, blank=True)
    harvest_timestamp = models.DateTimeField(null=True, blank=True)
    availability_start = models.DateField()
    availability_end = models.DateField()
    ped_eligible = models.BooleanField(default=False)
    ped_eligible_items = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=ListingStatus.choices, default=ListingStatus.ACTIVE)
    scratch_cooking_ready = models.BooleanField(default=False)
    source = models.CharField(max_length=50, default="self_service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "listings"

    def __str__(self):
        return f"{self.crop_name} — {self.farm}"


class NMCounty(models.Model):
    county_name = models.TextField(primary_key=True)
    county_seat = models.TextField()
    region = models.TextField()
    population_2020 = models.IntegerField(null=True, blank=True)
    area_sq_miles = models.IntegerField(null=True, blank=True)
    centroid_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    centroid_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rural_urban_class = models.TextField(null=True, blank=True)
    food_insecurity_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    child_food_insecurity_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    free_reduced_lunch_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_hispanic = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pct_native_american = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    num_farms_usda = models.IntegerField(null=True, blank=True)
    num_school_districts = models.IntegerField(null=True, blank=True)
    # is_high_priority is a computed column in Postgres; replicated here as a property
    data_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "nm_counties"

    def __str__(self):
        return str(self.county_name)

    @property
    def is_high_priority(self) -> bool:
        return self.food_insecurity_rate_pct is not None and self.food_insecurity_rate_pct >= 18.0


class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="requests")
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="requests")
    quantity_requested = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    requested_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "requests"

    def __str__(self):
        return f"Request {self.id} — {self.buyer} for {self.listing}"