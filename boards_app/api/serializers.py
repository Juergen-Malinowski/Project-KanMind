from rest_framework import serializers
from django.contrib.auth import get_user_model

from boards_app.models import Board
from tasks_app.models import Task


User = get_user_model()


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for a board list view"""

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a board."""

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = ["title", "members"]

    def create(self, validated_data):
        """Create a board with owner and members."""

        members = validated_data.pop("members", [])
        user = self.context["request"].user

        board = Board.objects.create(
            owner=user,
            **validated_data
        )

        if members:
            board.members.set(members)
        
        return board


class UserMinimalSerializer(serializers.ModelSerializer):
    """Serializer for minimal user data."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskInBoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for task data inside board detail view"""

    assignee = UserMinimalSerializer(read_only=True, allow_null=True)
    reviewer = UserMinimalSerializer(read_only=True, allow_null=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for board detail view with members and tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserMinimalSerializer(many=True, read_only=True)
    tasks = TaskInBoardDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer für updating board title and members."""

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = ["title", "members"]

    def update(self, instance, validated_data):
        """Update board title and members"""

        members = validated_data.pop("members", None)

        # Update title (if available)
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        # Replace all members (if provided)
        if members is not None:
            instance.members.set(members)
        
        return instance