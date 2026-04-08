from django.contrib import admin

from .models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for task model."""

    list_display = (
        "id",
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "reviewer",
        "due_date",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "priority",
        "due_date",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "title",
        "description",
        "board__title",
        "assignee__email",
        "reviewer__email",
    )
    filter_horizontal = ("members",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("id",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for comment model."""

    list_display = ("id", "task", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__email", "task__title")
    readonly_fields = ("created_at",)
    ordering = ("id",)
