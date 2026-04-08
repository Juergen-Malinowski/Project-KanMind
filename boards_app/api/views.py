from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from boards_app.models import Board
from .serializers import BoardListSerializer


class BoardListView(generics.ListAPIView):
    """API view to list boards for the authenticated user"""

    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

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
    

class BoardView(APIView):
    # Klärung später, ob für GET und POST eine oder zwei Views sinnvoll !
    pass


class BoardDetailView(APIView):
    # für <int:board_id>/ später klären ob GET, UPDATE und DELETE in einer View sinnvoll !
    pass