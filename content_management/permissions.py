from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    SAFE_METHODS,
    AllowAny,
)


class ReadOnly(AllowAny):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        self.message = 'User has read access only.'
        return False


class IsComplianceUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        perm = True
        if request.method in SAFE_METHODS:
            return True
        else:
            if not ( bool(request.user and request.user.is_authenticated)
                    and request.user.user_type == 'compliance_user' ):
                perm = False
        return perm
    

class IsContentCreatorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        perm = True
        if request.method in SAFE_METHODS:
            perm = True
        else:
            if not ( bool(request.user and request.user.is_authenticated)
                    and request.user.user_type == 'author' ):
                perm = False
                self.message = 'Read only access allowed for users who are not authors.'
        return perm

    def has_object_permission(self, request, view, obj):
        perm = super().has_object_permission(request, view, obj)
        if obj.created_by != request.user \
            and request.method not in SAFE_METHODS:
            perm = False
            self.message = 'Only read only access allowed for \
                  users other than the creator.'
        return perm


class IsReviewer(IsAuthenticated):
    def has_permission(self, request, view):
        perm = super().has_permission(request, view)
        if perm:
            if not request.user.user_type == 'reviewer':
                perm = False
        return perm