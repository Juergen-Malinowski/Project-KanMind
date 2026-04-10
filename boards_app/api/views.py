from django.db.models import Count, Prefetch, Q

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task

from .serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)


class BoardListCreateView(generics.ListCreateAPIView):
    """API view to list and create boards."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return serializer depending on request method."""
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer
    
    def get_queryset(self):
        """Return filtered and annotated boards."""

        user = self.request.user

        accessible_board_ids = Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).values_list("id", flat=True)

        queryset = (
            Board.objects.filter(id__in=accessible_board_ids)
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks",
                    filter=Q(tasks__status="to-do"),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    "tasks",
                    filter=Q(tasks__priority="high"),
                    distinct=True,
                ),
            )
        )

        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create board and return annotated response."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.save()

        board = (
            Board.objects.filter(id=board.id)
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks",
                    filter=Q(tasks__status="to-do"),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    "tasks",
                    filter=Q(tasks__priority="high"),
                    distinct=True,
                ),
            )
            .first()
        )

        response_serializer = BoardListSerializer(board)

        return Response(response_serializer.data, status=201)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update and delete a board."""

    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "board_id"

    def get_serializer_class(self):
        """Return serializer depending on request method."""

        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer
    
    def get_queryset(self):
        """Return queryset with related data for board detail."""

        task_queryset = Task.objects.select_related(
            "assignee",
            "reviewer",
        ).annotate(
            comments_count=Count("comments")
        )

        return Board.objects.select_related(
            "owner"
        ).prefetch_related(
            "members",
            Prefetch("tasks", queryset=task_queryset),
        ).distinct()

    def get_object(self):
        """Return board and enforce method-specific permission."""

        board = super().get_object()
        user = self.request.user

        if self.request.method in ["GET", "PATCH"]:
            if board.owner != user and not board.members.filter(id=user.id).exists():
                raise PermissionDenied(
                    "You must be the owner or a member of this board."
                )
        
        if self.request.method == "DELETE":
            if board.owner != user:
                raise PermissionDenied(
                    "Only the owner can delete this board."
                )
            
        return board