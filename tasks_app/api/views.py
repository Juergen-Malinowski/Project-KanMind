from django.db.models import Count

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks_app.models import Task

from .serializers import (
    TaskBaseSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
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
        
        task = serializer.save(created_by=request.user)

        task = Task.objects.filter(id=task.id).select_related(
            "board",
            "assignee",
            "reviewer",
        ).annotate(
            comments_count=Count("comments")
        ).first()

        response_serializer = TaskBaseSerializer(task)

        return Response(response_serializer.data, status=201)




class TaskDetailView(generics.GenericAPIView):
    """API view to update and delete a task."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskUpdateSerializer
    lookup_url_kwarg = "task_id"

    def get_task(self):
        """Return task with related objects and permissions context."""

        task_id = self.kwargs.get(self.lookup_url_kwarg)

        return Task.objects.filter(id=task_id).select_related(
            "board",
            "assignee",
            "reviewer",
            "created_by",
        ).annotate(
            comments_count=Count("comments")
        ).first()
    
    def patch(self, request, *args, **kwargs):
        """Update task and return serialized task response."""

        task = self.get_task()

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        is_board_member = task.board.members.filter(id=user.id).exists()
        is_board_owner = task.board.owner_id == user.id

        if not is_board_member and not is_board_owner:
            raise PermissionDenied(
                "You must be the owner or a member of this board."
            )
        
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task = Task.objects.filter(id=task.id).select_related(
            "board",
            "assignee",
            "reviewer",
            "created_by",
        ).annotate(
            comments_count=Count("comments")
        ).first()

        response_serializer = TaskBaseSerializer(task)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        """Delete task if the user is allowed to do so."""

        task = self.get_task()

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        user = request.user

        is_creator = task.created_by_id == user.id
        is_board_owner = task.board.owner_id == user.id

        # Only the creator or the board owner is allowed to delete this task.
        if not is_creator and not is_board_owner:
            return Response(
                {"detail": "Only the creator or the board owner can delete this task."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        task.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentView(APIView):
    pass


class CommentDetailView(APIView):
    pass
