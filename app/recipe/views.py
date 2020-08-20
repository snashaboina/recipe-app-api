from rest_framework import viewsets, mixins
from recipe.serializers import TagSerializers
from rest_framework import authentication, permissions
from core.models import Tag


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the database"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializers

    def get_queryset(self):
        """Limiting tags to authenticated current user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
