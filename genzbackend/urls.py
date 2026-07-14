"""
URL configuration for genzbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/wallets/", include("apps.wallets.urls")),
    path("api/referrals/", include("apps.referrals.urls")),
    path("api/mpesa/", include("apps.mpesa.urls")),
    path("api/campaigns/", include("apps.campaigns.urls")),
    path(
        "api/deriv/",
        include("apps.deriv.urls"),
    ),
]
