from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def check_board_owner_or_member_permission(board, user):
    """Check whether user is board owner or board member."""

    is_board_member = board.members.filter(id=user.id).exists()
    is_board_owner = board.owner_id == user.id

    if not is_board_member and not is_board_owner:
        raise PermissionDenied(
            "You must be the owner or a member of this board."   
        )
    
    
class IsBoardOwnerOrMember(BasePermission):
    """Allow access only to board owner or board members."""

    message = "You must be the owner or a member of this board." 

    def has_object_permission(self, request, view, obj):
        """Return whether user owns the board or a board member."""

        is_board_member = obj.members.filter(id=request.user.id).exists()
        is_board_owner = obj.owner_id == request.user.id

        return is_board_member or is_board_owner


def check_board_delete_permission(board, user):
    """Check whether user is allowed to delete the board."""

    if board.owner != user:
        raise PermissionDenied(
            "Only the owner can delete this board."
        )