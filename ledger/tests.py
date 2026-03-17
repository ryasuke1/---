from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import CashFlowEntryForm
from .models import CashFlowEntry, Category, OperationType, Status, Subcategory


class CashFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status = Status.objects.get(name='Бизнес')
        cls.income = OperationType.objects.get(name='Пополнение')
        cls.expense = OperationType.objects.get(name='Списание')
        cls.sales = Category.objects.get(name='Продажи', operation_type=cls.income)
        cls.marketing = Category.objects.get(name='Маркетинг', operation_type=cls.expense)
        cls.marketplace = Subcategory.objects.get(name='Маркетплейсы', category=cls.sales)
        cls.farpost = Subcategory.objects.get(name='Farpost', category=cls.marketing)

    def test_category_must_match_operation_type(self):
        entry = CashFlowEntry(
            created_at='2026-03-17',
            status=self.status,
            operation_type=self.income,
            category=self.marketing,
            subcategory=self.farpost,
            amount=Decimal('1500.00'),
        )

        with self.assertRaises(ValidationError) as error:
            entry.full_clean()

        self.assertIn('category', error.exception.message_dict)

    def test_subcategory_must_match_category(self):
        entry = CashFlowEntry(
            created_at='2026-03-17',
            status=self.status,
            operation_type=self.expense,
            category=self.marketing,
            subcategory=self.marketplace,
            amount=Decimal('1500.00'),
        )

        with self.assertRaises(ValidationError) as error:
            entry.full_clean()

        self.assertIn('subcategory', error.exception.message_dict)

    def test_entry_form_limits_subcategories_for_selected_category(self):
        form = CashFlowEntryForm(
            data={
                'created_at': '2026-03-17',
                'status': self.status.pk,
                'operation_type': self.expense.pk,
                'category': self.marketing.pk,
                'subcategory': self.farpost.pk,
                'amount': '2500.00',
            }
        )

        self.assertQuerySetEqual(
            form.fields['subcategory'].queryset.order_by('pk'),
            Subcategory.objects.filter(category=self.marketing).order_by('pk'),
            transform=lambda item: item,
        )

    def test_list_view_filters_entries_by_type(self):
        CashFlowEntry.objects.create(
            created_at='2026-03-17',
            status=self.status,
            operation_type=self.expense,
            category=self.marketing,
            subcategory=self.farpost,
            amount=Decimal('900.00'),
            comment='Расход на маркетинг',
        )
        CashFlowEntry.objects.create(
            created_at='2026-03-18',
            status=self.status,
            operation_type=self.income,
            category=self.sales,
            subcategory=self.marketplace,
            amount=Decimal('5000.00'),
            comment='Поступление от продажи',
        )

        response = self.client.get(reverse('ledger:entry-list'), {'operation_type': self.expense.pk})

        self.assertContains(response, 'Расход на маркетинг')
        self.assertNotContains(response, 'Поступление от продажи')
