from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardCreateSerializer


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


class BoardDetailView(APIView):
    # für <int:board_id>/ später klären ob GET, UPDATE und DELETE in einer View sinnvoll !
    pass