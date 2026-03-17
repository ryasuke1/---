from django.db import migrations


def seed_reference_data(apps, schema_editor):
    Status = apps.get_model('ledger', 'Status')
    OperationType = apps.get_model('ledger', 'OperationType')
    Category = apps.get_model('ledger', 'Category')
    Subcategory = apps.get_model('ledger', 'Subcategory')

    for name in ('Бизнес', 'Личное', 'Налог'):
        Status.objects.get_or_create(name=name)

    income, _ = OperationType.objects.get_or_create(name='Пополнение')
    expense, _ = OperationType.objects.get_or_create(name='Списание')

    income_categories = {
        'Продажи': ('Маркетплейсы', 'Клиенты'),
        'Инвестиции': ('Возврат', 'Займ учредителя'),
    }
    expense_categories = {
        'Инфраструктура': ('VPS', 'Proxy'),
        'Маркетинг': ('Farpost', 'Avito'),
    }

    for category_name, subcategories in income_categories.items():
        category, _ = Category.objects.get_or_create(name=category_name, operation_type=income)
        for subcategory_name in subcategories:
            Subcategory.objects.get_or_create(name=subcategory_name, category=category)

    for category_name, subcategories in expense_categories.items():
        category, _ = Category.objects.get_or_create(name=category_name, operation_type=expense)
        for subcategory_name in subcategories:
            Subcategory.objects.get_or_create(name=subcategory_name, category=category)


class Migration(migrations.Migration):
    dependencies = [
        ('ledger', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_reference_data, migrations.RunPython.noop),
    ]
