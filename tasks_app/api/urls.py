from django.urls import path

from .views import (
    AssignedToMeTaskView,
    CommentDeleteView,
    CommentShowAndPostView,
    ReviewingTaskView,
    TaskDetailView,
    TaskView,
)

urlpatterns = [
    path('assigned-to-me/', AssignedToMeTaskView.as_view(), name='tasks-assigned-to-me'),
    path('reviewing/', ReviewingTaskView.as_view(), name='tasks-reviewing'),
    path('', TaskView.as_view(), name='tasks'),
    path('<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/comments/', CommentShowAndPostView.as_view(), name='task-comments'),
    path(
        '<int:task_id>/comments/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='task-comment-detail'
    ),
]