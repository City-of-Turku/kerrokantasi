from rest_framework import serializers, viewsets

from democracy.pagination import DefaultLimitPagination
from democracy.models import AuthMethod


class AuthMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthMethod
        fields = ('id', 'name', 'amr')


class AuthMethodViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthMethodSerializer
    queryset = AuthMethod.objects.all()
    pagination_class = DefaultLimitPagination
