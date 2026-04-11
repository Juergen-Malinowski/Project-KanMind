from rest_framework.permissions import BasePermission


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow access only to task creator or board owner."""

    message = "Only the creator or the board owner can delete this task."

    def has_object_permission(self, request, view, obj):
        """Return whether user may delete the task."""

        is_creator = obj.created_by_id == request.user.id
        is_board_owner = obj.board.owner_id == request.user.id

        return is_creator or is_board_owner
    
    
class IsBoardOwnerOrMember(BasePermission):
    """Allow access only to board owner or board members."""

    message = "You must be the owner or a member of this board."

    def has_object_permission(self, request, view, obj):
        """Return whether user owns the board or is a board member."""

        is_board_member = obj.members.filter(id=request.user.id).exists()
        is_board_owner = obj.owner_id == request.user.id

        return is_board_member or is_board_owner


class IsCommentAuthor(BasePermission):
    """Allow access only to the author of the comment."""

    message = "Only the creator of this comment can delete it."

    def has_object_permission(self, request, view, obj):
        """Return whether user is the author of the comment."""

        return obj.author_id == request.user.id