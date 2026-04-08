from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin configuration for board model."""

    list_display = ("id", "title", "owner", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "owner__email", "owner__fullname")
    filter_horizontal = ("members",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("id",)
