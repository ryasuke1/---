from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import CashFlowEntry, Category, OperationType, Status, Subcategory


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('id', 'name')


class OperationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationType
        fields = ('id', 'name')


class CategorySerializer(serializers.ModelSerializer):
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'operation_type', 'operation_type_name')


class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    operation_type_id = serializers.IntegerField(source='category.operation_type_id', read_only=True)

    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'category', 'category_name', 'operation_type_id')


class CashFlowEntrySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = CashFlowEntry
        fields = (
            'id',
            'created_at',
            'status',
            'status_name',
            'operation_type',
            'operation_type_name',
            'category',
            'category_name',
            'subcategory',
            'subcategory_name',
            'amount',
            'comment',
            'created_on',
            'updated_on',
        )

    def validate(self, attrs):
        instance = self.instance or CashFlowEntry()

        for field, value in attrs.items():
            setattr(instance, field, value)

        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

        return attrs
