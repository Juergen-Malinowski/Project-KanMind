from django.db.models import Count

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
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


def get_task_with_related_data(task_id):
    """
    Return task with related objects and comment count.

    Used to keep task response queries reusable across task views.
    """

    return Task.objects.filter(id=task_id).select_related(
        "board",
        "assignee",
        "reviewer",
        "created_by",
    ).annotate(
        comments_count=Count("comments")
    ).first()


class AssignedToMeTaskView(generics.ListAPIView):
    """API view to list tasks assigned to the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskBaseSerializer

    def get_queryset(self):
        """Return tasks assigned to the authenticated user."""

        return Task.objects.filter(
            assignee=self.request.user
        ).select_related(
            # Use select_related (joins) and annotate (aggregations) for
            # performance optimization
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

    def get_board(self, board_id):
        """
        Return board object by ID or None if it does not exist.

        Used for manual 404 handling during task creation.
        """

        return Board.objects.filter(id=board_id).first()

    def get_member_validation_error(self, board, user, field_name):
        """
        Return validation response if user is not a board member.

        Keeps member checks reusable for assignee and reviewer validation.
        """

        if user and not board.members.filter(id=user.id).exists():
            return Response(
                {
                    field_name: (
                        f"{field_name.replace('_id', '').capitalize()} must "
                        f"be a board member."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def get_assignment_validation_error(self, board, data):
        """
        Return validation response for invalid assignee or reviewer.

        Combines both assignment checks to keep create() compact.
        """

        assignee_error = self.get_member_validation_error(
            board,
            data.get("assignee"),
            "assignee_id",
        )
        if assignee_error:
            return assignee_error

        reviewer_error = self.get_member_validation_error(
            board,
            data.get("reviewer"),
            "reviewer_id",
        )
        if reviewer_error:
            return reviewer_error

        return None

    def create(self, request, *args, **kwargs):
        """
        Create task and return serialized task response.

        Handles manual board lookup to return 404 for missing boards.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        board = self.get_board(data["board"])

        if board is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, board)

        validation_error = self.get_assignment_validation_error(board, data)
        if validation_error:
            return validation_error

        task = serializer.save(board=board, created_by=request.user)
        task = get_task_with_related_data(task.id)
        response_serializer = TaskBaseSerializer(task)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
        """
        Return task with related objects and permissions context.

        Uses shared query helper to avoid duplicated task response logic.
        """

        task_id = self.kwargs.get(self.lookup_url_kwarg)

        return get_task_with_related_data(task_id)

    def patch(self, request, *args, **kwargs):
        """Update task and return serialized task response."""

        task = self.get_task()

        if task is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, task.board)

        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task = get_task_with_related_data(task.id)

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
