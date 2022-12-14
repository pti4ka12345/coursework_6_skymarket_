from rest_framework import pagination, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from ads.filter import AdFilter
from ads.models import Ad, Comment
from ads.permissions import IsOwner
from ads.serializers import AdSerializer, CommentSerializer


class AdPagination(pagination.PageNumberPagination):
    page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = AdPagination
    permission_classes = (AllowAny)
    filter_backends = (DjangoFilterBackend)
    filterset_class = AdFilter

    def perform_create(self, serialazer):
        user = self.request.user
        serialazer.save(author=user)

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "update", "partial_update", "destroy"]:
            return AdSerializer

    def get_permissions(self):
        permission_classes = (AllowAny,)
        if self.action in ["retrieve"]:
            permission_classes = (AllowAny,)
        elif self.action in ["create", "update", "partial_update", "destroy", "me"]:
            permission_classes = (IsOwner | IsAdminUser)
        return tuple(permission() for permission in permission_classes)

    def get_queryset(self):
        if self.action == "me":
            return Ad.objects.filter(author=self.request.user).all()
        return Ad.objects.all()

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serialazer):
        ad_id = self.kwargs.get("ad_pk")
        ad_instance = get_object_or_404(Ad, id=ad_id)

    def get_permission(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated]
        return super(self.__class__, self).get_permissions()
