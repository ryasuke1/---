from rest_framework import viewsets

from .models import CashFlowEntry, Category, OperationType, Status, Subcategory
from .serializers import (
    CashFlowEntrySerializer,
    CategorySerializer,
    OperationTypeSerializer,
    StatusSerializer,
    SubcategorySerializer,
)


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.order_by('name')
    serializer_class = StatusSerializer


class OperationTypeViewSet(viewsets.ModelViewSet):
    queryset = OperationType.objects.order_by('name')
    serializer_class = OperationTypeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('operation_type').order_by('operation_type__name', 'name')
    serializer_class = CategorySerializer


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.select_related('category', 'category__operation_type').order_by(
        'category__name',
        'name',
    )
    serializer_class = SubcategorySerializer


class CashFlowEntryViewSet(viewsets.ModelViewSet):
    queryset = CashFlowEntry.objects.select_related(
        'status',
        'operation_type',
        'category',
        'subcategory',
    ).order_by('-created_at', '-id')
    serializer_class = CashFlowEntrySerializer
