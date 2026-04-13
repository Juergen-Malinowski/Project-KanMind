from django.db.models import Count, Prefetch, Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task

from .permissions import (
    IsBoardOwner,
    IsBoardOwnerOrMember,
)
from .serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardPatchResponseSerializer,
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

        # Collect accessible board IDs via values_list (method from
        # Django QuerySet) for later use in __in queries
        accessible_board_ids = Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).values_list("id", flat=True)

        queryset = (
            Board.objects.filter(id__in=accessible_board_ids)
            # Add calculated (aggregated) fields per board using annotate
            # (method from Django QuerySet) to avoid extra queries
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

    # Configure object lookup by "id" using "board_id" from URL
    lookup_field = "id"
    lookup_url_kwarg = "board_id"

    def get_permissions(self):
        """Return permission classes depending on request method."""

        if self.request.method in ["GET", "PATCH"]:

            # get_permissions() overrides permission_classes[],
            # therefore "IsAuthenticated()" must be explicitly included here ...
            return [IsAuthenticated(), IsBoardOwnerOrMember()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsBoardOwner()]
        
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return serializer depending on request method."""

        if self.request.method == "PATCH":
            return BoardUpdateSerializer

        return BoardDetailSerializer

    def get_queryset(self):
        """Return queryset with related data for board detail."""

        # Load related objects efficiently via select_related and
        # prefetch_related, then remove duplicates with distinct
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

        # Call parent get_object via super() to preserve built-in DRF behavior
        board = super().get_object()

        if self.request.method in ["GET", "PATCH"]:
            self.check_object_permissions(self.request, board)

        if self.request.method == "DELETE":
            self.check_object_permissions(self.request, board)

        return board

    def patch(self, request, *args, **kwargs):
        """Update board and return patch response data."""

        board = self.get_object()

        serializer = BoardUpdateSerializer(
            board,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = BoardPatchResponseSerializer(board)

        return Response(response_serializer.data, status=200)