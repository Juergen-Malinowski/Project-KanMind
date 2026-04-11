from rest_framework.exceptions import PermissionDenied


def check_board_owner_or_member_permission(board, user):
    """Check whether user is board owner or board member"""

    is_board_member = board.members.filter(id=user.id).exists()
    is_board_owner = board.owner_id == user.id

    if not is_board_member and not is_board_owner:
        raise PermissionDenied(
            "You must be the owner or a member of this board."
        )

def check_task_delete_permission(task, user):
    """Check whether user is allowed to delete the task."""

    is_creator = task.created_by_id == user.id
    is_board_owner = task.board.owner_id == user.id

    if not is_creator and not is_board_owner:
        raise PermissionDenied(
            "Only the creator or the board owner can delete this task."
        )

def check_comment_delete_permission(comment, user):
    """Check whether user is allowed to delete the comment."""

    if comment.author_id != user.id:
        raise PermissionDenied(
            "Only the creator of this comment can delete it."
        )