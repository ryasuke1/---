from django.contrib import admin

from .models import CashFlowEntry, Category, OperationType, Status, Subcategory


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'operation_type')
    list_filter = ('operation_type',)
    search_fields = ('name',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'operation_type')
    list_filter = ('category__operation_type', 'category')
    search_fields = ('name', 'category__name')

    @admin.display(description='Тип операции')
    def operation_type(self, obj):
        return obj.category.operation_type


@admin.register(CashFlowEntry)
class CashFlowEntryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'status', 'operation_type', 'category', 'subcategory', 'amount')
    list_filter = ('status', 'operation_type', 'category', 'subcategory', 'created_at')
    search_fields = ('comment', 'category__name', 'subcategory__name')
    date_hierarchy = 'created_at'
