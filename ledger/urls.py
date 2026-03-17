from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import CashFlowEntryViewSet, CategoryViewSet, OperationTypeViewSet, StatusViewSet, SubcategoryViewSet
from .views import (
    CashFlowEntryCreateView,
    CashFlowEntryDeleteView,
    CashFlowEntryUpdateView,
    CashFlowListView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryUpdateView,
    OperationTypeCreateView,
    OperationTypeDeleteView,
    OperationTypeUpdateView,
    ReferenceOverviewView,
    StatusCreateView,
    StatusDeleteView,
    StatusUpdateView,
    SubcategoryCreateView,
    SubcategoryDeleteView,
    SubcategoryUpdateView,
)

app_name = 'ledger'

router = DefaultRouter()
router.register('statuses', StatusViewSet, basename='status-api')
router.register('operation-types', OperationTypeViewSet, basename='operation-type-api')
router.register('categories', CategoryViewSet, basename='category-api')
router.register('subcategories', SubcategoryViewSet, basename='subcategory-api')
router.register('entries', CashFlowEntryViewSet, basename='entry-api')

urlpatterns = [
    path('', CashFlowListView.as_view(), name='entry-list'),
    path('entries/new/', CashFlowEntryCreateView.as_view(), name='entry-create'),
    path('entries/<int:pk>/edit/', CashFlowEntryUpdateView.as_view(), name='entry-update'),
    path('entries/<int:pk>/delete/', CashFlowEntryDeleteView.as_view(), name='entry-delete'),
    path('references/', ReferenceOverviewView.as_view(), name='reference-overview'),
    path('references/statuses/new/', StatusCreateView.as_view(), name='status-create'),
    path('references/statuses/<int:pk>/edit/', StatusUpdateView.as_view(), name='status-update'),
    path('references/statuses/<int:pk>/delete/', StatusDeleteView.as_view(), name='status-delete'),
    path('references/operation-types/new/', OperationTypeCreateView.as_view(), name='operation-type-create'),
    path(
        'references/operation-types/<int:pk>/edit/',
        OperationTypeUpdateView.as_view(),
        name='operation-type-update',
    ),
    path(
        'references/operation-types/<int:pk>/delete/',
        OperationTypeDeleteView.as_view(),
        name='operation-type-delete',
    ),
    path('references/categories/new/', CategoryCreateView.as_view(), name='category-create'),
    path('references/categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-update'),
    path('references/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('references/subcategories/new/', SubcategoryCreateView.as_view(), name='subcategory-create'),
    path('references/subcategories/<int:pk>/edit/', SubcategoryUpdateView.as_view(), name='subcategory-update'),
    path('references/subcategories/<int:pk>/delete/', SubcategoryDeleteView.as_view(), name='subcategory-delete'),
    path('api/', include(router.urls)),
]
