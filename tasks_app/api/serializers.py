from rest_framework import serializers

from boards_app.api.serializers import UserMinimalSerializer
from tasks_app.models import Task


class TaskBaseSerializer(serializers.ModelSerializer):
    """Base serializer for task list responses."""

    assignee = UserMinimalSerializer(read_only=True, allow_null=True)
    reviewer = UserMinimalSerializer(read_only=True, allow_null=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class AssignedToMeTaskSerializer(TaskBaseSerializer):
    """
    Serializer for tasks assigned to the authenticated user.

    Inherits all fields from TaskBaseSerializer.
    """


class ReviewingTaskSerializer(TaskBaseSerializer):
    """
    Serializer for tasks reviewed by the authenticated user.

    Inherits all fields from TaskBaseSerializer.
    """