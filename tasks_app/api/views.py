from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from tasks_app.models import Task
from .serializers import (
    AssignedToMeTaskSerializer, ReviewingTaskSerializer
)


class AssignedToMeTaskView(generics.ListAPIView):
    """API view to list tasks assigned to the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = AssignedToMeTaskSerializer

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
    serializer_class = ReviewingTaskSerializer

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


class TaskView(APIView):
    pass


class TaskDetailView(APIView):
    pass


class TaskCommentView(APIView):
    pass


class CommentDetailView(APIView):
    pass