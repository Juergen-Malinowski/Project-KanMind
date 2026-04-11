from rest_framework.permissions import BasePermission

    
class IsBoardOwnerOrMember(BasePermission):
    """Allow access only to board owner or board members."""

    message = "You must be the owner or a member of this board." 

    def has_object_permission(self, request, view, obj):
        """Return whether user owns the board or a board member."""

        is_board_member = obj.members.filter(id=request.user.id).exists()
        is_board_owner = obj.owner_id == request.user.id

        return is_board_member or is_board_owner


class IsBoardOwner(BasePermission):
    """Allow access only to the owner of the board."""

    message = "Only the owner can delete this board."

    def has_object_permission(self, request, view, obj):
        """Return whether user is the owner of the board."""

        return obj.owner_id == request.user.id