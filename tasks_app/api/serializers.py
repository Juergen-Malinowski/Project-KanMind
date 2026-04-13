from django.contrib.auth import get_user_model

from rest_framework import serializers

from boards_app.api.serializers import UserMinimalSerializer
from boards_app.models import Board
from tasks_app.models import Comment, Task


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
    """
    Serializer for creating a task; uses IntegerField for board to allow
    manual 404 handling in view instead of automatic 400 validation in serializer.
    """

    board = serializers.IntegerField(write_only=True)
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


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a task."""

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

        board = self.instance.board
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


class CommentShowSerializer(serializers.ModelSerializer):
    """Serializer for comment response."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]

    def get_author(self, obj):
        """Return the full name of the comment author."""

        return obj.author.fullname


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a comment."""

    class Meta:
        model = Comment
        fields = [
            "content",
        ]

    def validate_content(self, value):
        """Validate that comment is not empty."""

        cleaned_value = value.strip()

        if not cleaned_value:
            raise serializers.ValidationError(
                "This field may not be blank."
            )

        return cleaned_value