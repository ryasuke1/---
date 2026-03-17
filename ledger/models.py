from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class NamedReference(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Status(NamedReference):
    class Meta(NamedReference.Meta):
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class OperationType(NamedReference):
    class Meta(NamedReference.Meta):
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'


class Category(models.Model):
    name = models.CharField('Название', max_length=120)
    operation_type = models.ForeignKey(
        OperationType,
        verbose_name='Тип операции',
        related_name='categories',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('operation_type__name', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('operation_type', 'name'),
                name='unique_category_per_operation_type',
            ),
        ]

    def __str__(self):
        return f'{self.name} [{self.operation_type.name}]'


class Subcategory(models.Model):
    name = models.CharField('Название', max_length=120)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='subcategories',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ('category__name', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('category', 'name'),
                name='unique_subcategory_per_category',
            ),
        ]

    def __str__(self):
        return f'{self.name} [{self.category.name}]'


class CashFlowEntry(models.Model):
    created_at = models.DateField('Дата операции', default=timezone.localdate)
    status = models.ForeignKey(
        Status,
        verbose_name='Статус',
        related_name='entries',
        on_delete=models.PROTECT,
    )
    operation_type = models.ForeignKey(
        OperationType,
        verbose_name='Тип',
        related_name='entries',
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='entries',
        on_delete=models.PROTECT,
    )
    subcategory = models.ForeignKey(
        Subcategory,
        verbose_name='Подкатегория',
        related_name='entries',
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField('Сумма, руб.', max_digits=12, decimal_places=2)
    comment = models.TextField('Комментарий', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ('-created_at', '-id')

    def __str__(self):
        return f'{self.created_at:%d.%m.%Y} · {self.amount} ₽ · {self.category.name}'

    def clean(self):
        errors = {}

        if self.amount is not None and self.amount <= 0:
            errors['amount'] = 'Сумма должна быть больше нуля.'

        if self.category_id and self.operation_type_id:
            if self.category.operation_type_id != self.operation_type_id:
                errors['category'] = 'Категория должна относиться к выбранному типу операции.'

        if self.subcategory_id and self.category_id:
            if self.subcategory.category_id != self.category_id:
                errors['subcategory'] = 'Подкатегория должна относиться к выбранной категории.'

        if errors:
            raise ValidationError(errors)

    @property
    def amount_rub(self):
        return f'{self.amount:,.2f}'.replace(',', ' ').replace('.', ',')
