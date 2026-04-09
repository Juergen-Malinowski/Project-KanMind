from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.api.serializers import UserMinimalSerializer
from tasks_app.models import Task
from boards_app.models import Board


User = get_user_model()


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


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a task."""

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]
    
    def validate(self, attrs):
        """Validate board members for assignee and reviewer."""

        board = attrs.get("board")
        assignee = attrs.get("assignee")
        reviewer = attrs.get("reviewer")

        if assignee and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                {"assignee_id": "Assignee must be a board member."}
            )
        
        if reviewer and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError(
                {"reviewer_id": "Reviewer must be a board member."}
            )
        
        return attrs
