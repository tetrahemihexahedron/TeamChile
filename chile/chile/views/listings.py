from django.http import Http404, HttpResponse

from chile.models import Farm


def create_listing(request, farm_id):
    farm = Farm.objects.first()
    if farm is None:
        raise Http404("No farms in the database yet")
    return HttpResponse(
        f"Form to create a new listing goes here (stub: using farm {farm.name!r})"
    )
