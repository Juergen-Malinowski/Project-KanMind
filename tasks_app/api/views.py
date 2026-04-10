from django.db.models import Count

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks_app.models import Comment, Task

from .serializers import (
    CommentCreateSerializer, 
    CommentShowSerializer,
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


class CommentShowAndPostView(APIView):
    """API view to list and create comments for a task."""

    permission_classes = [IsAuthenticated]

    def get_task(self, task_id):
        """Return task object."""

        return Task.objects.filter(id=task_id).select_related(
            "board"
        ).first()
    
    def check_board_permission(self, task, user):
        """Check if user is board member or owner."""

        is_member = task.board.members.filter(id=user.id).exists()
        is_owner = task.board.owner_id == user.id

        if not is_member and not is_owner:
            raise PermissionDenied(
                "You must be a member or the owner of this board."
            )
        
    def get(self, request, task_id):

        task = self.get_task(task_id)

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.check_board_permission(task, request.user)

        comments = task.comments.select_related("author").all()

        serializer = CommentShowSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, task_id):
        """Create a new comment for a task."""

        task = self.get_task(task_id)

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.check_board_permission(task, request.user)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            task=task,
            author=request.user,
        )

        response_serializer = CommentShowSerializer(comment)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CommentDeleteView(APIView):
    """API view to delete a comment of a task."""

    permission_classes = [IsAuthenticated]

    def get_comment(self, task_id, comment_id):
        """Return comment object for the given task."""

        return Comment.objects.filter(
            id=comment_id,
            task_id=task_id,
        ).select_related(
            "author",
            "task",
        ).first()
    
    def delete(self, request, task_id, comment_id):
        """Delete comment if the user is the author."""

        comment = self.get_comment(task_id, comment_id)

        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if comment.author_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "Only the creator of this comment can delete it."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
