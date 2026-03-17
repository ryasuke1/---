from django.contrib import messages
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import (
    CashFlowEntryForm,
    CashFlowFilterForm,
    CategoryForm,
    OperationTypeForm,
    StatusForm,
    SubcategoryForm,
)
from .models import CashFlowEntry, Category, OperationType, Status, Subcategory


def dependency_payload():
    return {
        'categories_payload': list(
            Category.objects.select_related('operation_type')
            .order_by('operation_type__name', 'name')
            .values('id', 'name', 'operation_type_id')
        ),
        'subcategories_payload': list(
            Subcategory.objects.select_related('category')
            .order_by('category__name', 'name')
            .values('id', 'name', 'category_id')
        ),
    }


def missing_references():
    missing = []

    if not Status.objects.exists():
        missing.append('статусы')
    if not OperationType.objects.exists():
        missing.append('типы операций')
    if not Category.objects.exists():
        missing.append('категории')
    if not Subcategory.objects.exists():
        missing.append('подкатегории')

    return missing


class DependencyContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dependency_payload())
        return context


class CashFlowListView(DependencyContextMixin, ListView):
    model = CashFlowEntry
    template_name = 'ledger/entry_list.html'
    context_object_name = 'entries'

    def get_queryset(self):
        queryset = CashFlowEntry.objects.select_related(
            'status',
            'operation_type',
            'category',
            'subcategory',
        )
        self.filter_form = CashFlowFilterForm(self.request.GET or None)
        return self.filter_form.filter_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_amount = self.object_list.aggregate(total=Sum('amount'))['total']
        context.update(
            filter_form=self.filter_form,
            total_amount=total_amount,
            entries_count=self.object_list.count(),
            status_count=Status.objects.count(),
            operation_type_count=OperationType.objects.count(),
            category_count=Category.objects.count(),
            subcategory_count=Subcategory.objects.count(),
            missing_reference_data=missing_references(),
        )
        return context


class CashFlowEntryViewMixin(DependencyContextMixin):
    model = CashFlowEntry
    form_class = CashFlowEntryForm
    template_name = 'ledger/entry_form.html'
    success_url = reverse_lazy('ledger:entry-list')
    success_message = ''
    page_title = ''
    page_intro = ''
    submit_label = ''

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            page_intro=self.page_intro,
            submit_label=self.submit_label,
            cancel_url=self.success_url,
            missing_reference_data=missing_references(),
        )
        return context


class CashFlowEntryCreateView(CashFlowEntryViewMixin, CreateView):
    page_title = 'Новая запись ДДС'
    page_intro = 'Зафиксируйте поступление или списание с проверкой всех зависимостей.'
    submit_label = 'Сохранить запись'
    success_message = 'Запись успешно создана.'


class CashFlowEntryUpdateView(CashFlowEntryViewMixin, UpdateView):
    page_title = 'Редактирование записи'
    page_intro = 'Обновите данные операции. Бизнес-правила проверятся при сохранении.'
    submit_label = 'Сохранить изменения'
    success_message = 'Запись успешно обновлена.'


class CashFlowEntryDeleteView(DeleteView):
    model = CashFlowEntry
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:entry-list')

    def form_valid(self, form):
        messages.success(self.request, 'Запись удалена.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление записи',
            page_intro='Действие необратимо. Проверьте данные операции перед удалением.',
            cancel_url=self.success_url,
            object_label='запись ДДС',
        )
        return context


class ReferenceOverviewView(TemplateView):
    template_name = 'ledger/reference_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            statuses=Status.objects.order_by('name'),
            operation_types=OperationType.objects.order_by('name'),
            categories=Category.objects.select_related('operation_type').order_by('operation_type__name', 'name'),
            subcategories=Subcategory.objects.select_related(
                'category',
                'category__operation_type',
            ).order_by('category__operation_type__name', 'category__name', 'name'),
        )
        return context


class ReferenceFormMixin:
    template_name = 'ledger/reference_form.html'
    success_url = reverse_lazy('ledger:reference-overview')
    page_title = ''
    page_intro = ''
    submit_label = ''
    success_message = ''

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            page_intro=self.page_intro,
            submit_label=self.submit_label,
            cancel_url=self.success_url,
        )
        return context


class ProtectedDeleteMixin:
    success_url = reverse_lazy('ledger:reference-overview')
    protected_message = 'Удаление невозможно: объект используется в связанных данных.'
    success_message = 'Объект удалён.'

    def form_valid(self, form):
        self.object = self.get_object()

        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return HttpResponseRedirect(self.get_success_url())

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class StatusCreateView(ReferenceFormMixin, CreateView):
    model = Status
    form_class = StatusForm
    page_title = 'Новый статус'
    page_intro = 'Статусы используются для группировки операций по бизнес-смыслу.'
    submit_label = 'Сохранить статус'
    success_message = 'Статус создан.'


class StatusUpdateView(ReferenceFormMixin, UpdateView):
    model = Status
    form_class = StatusForm
    page_title = 'Редактирование статуса'
    page_intro = 'Изменения применятся ко всем операциям, связанным со статусом.'
    submit_label = 'Сохранить статус'
    success_message = 'Статус обновлён.'


class StatusDeleteView(ProtectedDeleteMixin, DeleteView):
    model = Status
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:reference-overview')
    success_message = 'Статус удалён.'
    protected_message = 'Нельзя удалить статус, пока он используется в записях.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление статуса',
            page_intro='Если статус используется в записях, база не даст удалить его по ошибке.',
            cancel_url=self.success_url,
            object_label='статус',
        )
        return context


class OperationTypeCreateView(ReferenceFormMixin, CreateView):
    model = OperationType
    form_class = OperationTypeForm
    page_title = 'Новый тип операции'
    page_intro = 'Тип определяет допустимые категории и общую природу движения средств.'
    submit_label = 'Сохранить тип'
    success_message = 'Тип операции создан.'


class OperationTypeUpdateView(ReferenceFormMixin, UpdateView):
    model = OperationType
    form_class = OperationTypeForm
    page_title = 'Редактирование типа операции'
    page_intro = 'Проверьте связанные категории перед сохранением изменений.'
    submit_label = 'Сохранить тип'
    success_message = 'Тип операции обновлён.'


class OperationTypeDeleteView(ProtectedDeleteMixin, DeleteView):
    model = OperationType
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:reference-overview')
    success_message = 'Тип операции удалён.'
    protected_message = 'Нельзя удалить тип операции, пока на него ссылаются категории или записи.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление типа операции',
            page_intro='Удаление запрещено, если на тип завязаны категории или записи.',
            cancel_url=self.success_url,
            object_label='тип операции',
        )
        return context


class CategoryCreateView(ReferenceFormMixin, CreateView):
    model = Category
    form_class = CategoryForm
    page_title = 'Новая категория'
    page_intro = 'Категория обязательно привязывается к типу операции.'
    submit_label = 'Сохранить категорию'
    success_message = 'Категория создана.'


class CategoryUpdateView(ReferenceFormMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    page_title = 'Редактирование категории'
    page_intro = 'Изменение типа операции повлияет на доступность категории в формах ДДС.'
    submit_label = 'Сохранить категорию'
    success_message = 'Категория обновлена.'


class CategoryDeleteView(ProtectedDeleteMixin, DeleteView):
    model = Category
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:reference-overview')
    success_message = 'Категория удалена.'
    protected_message = 'Нельзя удалить категорию, пока на неё ссылаются подкатегории или записи.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление категории',
            page_intro='Удаление запрещено, если в категории есть подкатегории или записи.',
            cancel_url=self.success_url,
            object_label='категорию',
        )
        return context


class SubcategoryCreateView(ReferenceFormMixin, CreateView):
    model = Subcategory
    form_class = SubcategoryForm
    page_title = 'Новая подкатегория'
    page_intro = 'Подкатегория всегда живёт внутри одной категории.'
    submit_label = 'Сохранить подкатегорию'
    success_message = 'Подкатегория создана.'


class SubcategoryUpdateView(ReferenceFormMixin, UpdateView):
    model = Subcategory
    form_class = SubcategoryForm
    page_title = 'Редактирование подкатегории'
    page_intro = 'Проверьте привязку к категории перед сохранением.'
    submit_label = 'Сохранить подкатегорию'
    success_message = 'Подкатегория обновлена.'


class SubcategoryDeleteView(ProtectedDeleteMixin, DeleteView):
    model = Subcategory
    template_name = 'ledger/confirm_delete.html'
    success_url = reverse_lazy('ledger:reference-overview')
    success_message = 'Подкатегория удалена.'
    protected_message = 'Нельзя удалить подкатегорию, пока она используется в записях.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление подкатегории',
            page_intro='Если подкатегория уже использована в операциях, удаление будет заблокировано.',
            cancel_url=self.success_url,
            object_label='подкатегорию',
        )
        return context
