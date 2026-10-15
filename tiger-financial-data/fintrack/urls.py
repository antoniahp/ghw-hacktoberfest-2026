from django.urls import path

from market import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/prices/", views.prices_api, name="prices_api"),
]
