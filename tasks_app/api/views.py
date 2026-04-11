from django.db.models import Count

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks_app.models import Comment, Task

from .permissions import (
    IsBoardOwnerOrMember,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)
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

    def get_permissions(self):
        """Return permission classes for task creation."""

        # get_permissions() overrides permission_classes,
        # therefore "IsAuthenticated()" must be explicitly included here ...
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def create(self, request, *args, **kwargs):
        """Create task and return serialized task response."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.validated_data["board"]
        self.check_object_permissions(request, board)
        
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

    def get_permissions(self):
        """Return permission classes depending on request method."""

        if self.request.method == "PATCH":

            # get_permissions() overrides permission_classes,
            # therefore "IsAuthenticated()" must be explicitly included here ...
            return [IsAuthenticated(), IsBoardOwnerOrMember()]    
        
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]    
        
        return [IsAuthenticated()]

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
        
        self.check_object_permissions(request, task.board)
        
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
        
        self.check_object_permissions(request, task)
        
        task.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentShowAndPostView(APIView):
    """API view to list and create comments for a task."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Return permission classes for comment list and creation."""

        # get_permissions() overrides permission_classes,
        # therefore "IsAuthenticated()" must be explicitly included here ...
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def get_task(self, task_id):
        """Return task object."""

        return Task.objects.filter(id=task_id).select_related(
            "board"
        ).first()
    
    def get(self, request, task_id):
        """Return all comments for a task."""

        task = self.get_task(task_id)

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, task.board)

        comments = task.comments.select_related("author").all()

        serializer = CommentShowSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, task_id):
        """Create a new comment for a task."""

        task = self.get_task(task_id)

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, task.board)

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

    def get_permissions(self):
        """Return permission classes for comment deletion."""

        # get_permissions() overrides permission_classes,
        # therefore "IsAuthenticated()" must be explicitly included here ...
        return [IsAuthenticated(), IsCommentAuthor()]

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
        
        self.check_object_permissions(request, comment)
        
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
