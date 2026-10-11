"""
URL configuration for finance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path

from tracker.views import (
    home,
    delete_transaction,
    edit_transaction,
    register_view,
    login_view,
    logout_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Transactions
    path("", home, name="home"),
    path("delete/<int:id>/", delete_transaction, name="delete_transaction"),
    path("edit/<int:id>/", edit_transaction, name="edit_transaction"),
]