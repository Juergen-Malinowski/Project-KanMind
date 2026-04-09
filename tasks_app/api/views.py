from django.db.models import Count
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks_app.models import Task
from .serializers import (
    TaskBaseSerializer, TaskCreateSerializer
)


class AssignedToMeTaskView(generics.ListAPIView):
    """API view to list tasks assigned to the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskBaseSerializer

    def get_queryset(self):
        """Return tasks assigned to the authenticated user."""    

        return Task.objects.filter(
            assignee=self.request.user
        ).select_related(
            "board",
            "assignee",
            "reviewer",
        ).annotate(
            comments_count=Count("comments")
        )
        
    


class ReviewingTaskView(generics.ListAPIView):
    """API view to list tasks reviewed by the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskBaseSerializer

    def get_queryset(self):
        """Return tasks reviewed by the authenticated user."""    

        return Task.objects.filter(
            reviewer=self.request.user
        ).select_related(
            "board",
            "assignee",
            "reviewer",
        ).annotate(
            comments_count=Count("comments")
        )


class TaskView(generics.CreateAPIView):
    """API view to create a task."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskCreateSerializer

    def create(self, request, *args, **kwargs):
        """Create task and return serialized task response."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.validated_data["board"]
        user = request.user

        is_board_member = board.members.filter(id=user.id).exists()
        is_board_owner = board.owner_id == user.id

        if not is_board_member and not is_board_owner:
            raise PermissionDenied(
                "You must be the owner or a member of this board."
            )
        
        task = serializer.save()

        task = Task.objects.filter(id=task.id).select_related(
            "board",
            "assignee",
            "reviewer",
        ).annotate(
            comments_count=Count("comments")
        ).first()

        response_serializer = TaskBaseSerializer(task)

        return Response(response_serializer.data, status=201)




class TaskDetailView(APIView):
    pass


class TaskCommentView(APIView):
    pass


class CommentDetailView(APIView):
    pass
