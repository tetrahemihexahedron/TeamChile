from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("listings/", views.market_view, name="market_view"),
    path("listings/<uuid:listing_id>/request/", views.request_submission, name="request_submission"),
    path("listings/create/", views.create_listing, name="create_listing"),
    path("farm/dashboard/", views.farm_dashboard, name="farm_dashboard"),
    path("buyer/dashboard/", views.buyer_dashboard, name="buyer_dashboard"),
    path("data/", views.data_page, name="data_page"),
    path("farm/requests/<uuid:request_id>/respond/", views.respond_request, name="respond_request"),
]
