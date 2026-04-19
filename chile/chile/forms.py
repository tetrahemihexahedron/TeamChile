from django import forms

from .models import Listing


_FIELD = {"class": "field-input"}


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("crop_name", "quantity_available")
        labels = {
            "crop_name": "Crop name",
            "quantity_available": "Quantity",
        }
        widgets = {
            "crop_name": forms.TextInput(
                attrs={**_FIELD, "placeholder": "e.g. Hatch green chiles"}
            ),
            "quantity_available": forms.NumberInput(
                attrs={**_FIELD, "step": "0.01", "min": "0", "inputmode": "decimal"}
            ),
        }
