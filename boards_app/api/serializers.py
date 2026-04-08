from rest_framework import serializers
from django.contrib.auth import get_user_model

from boards_app.models import Board


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