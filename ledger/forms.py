from django import forms

from .models import CashFlowEntry, Category, OperationType, Status, Subcategory


class DateInput(forms.DateInput):
    input_type = 'date'


def style_form(form):
    for field in form.fields.values():
        widget = field.widget
        existing_class = widget.attrs.get('class', '')
        base_class = 'input-control'
        widget.attrs['class'] = f'{existing_class} {base_class}'.strip()


class NamedReferenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
        self.fields['name'].widget.attrs['placeholder'] = 'Введите название'


class StatusForm(NamedReferenceForm):
    class Meta:
        model = Status
        fields = ('name',)


class OperationTypeForm(NamedReferenceForm):
    class Meta:
        model = OperationType
        fields = ('name',)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'operation_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operation_type'].queryset = OperationType.objects.order_by('name')
        style_form(self)
        self.fields['name'].widget.attrs['placeholder'] = 'Например, Маркетинг'


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ('name', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.select_related('operation_type').order_by(
            'operation_type__name',
            'name',
        )
        style_form(self)
        self.fields['name'].widget.attrs['placeholder'] = 'Например, Farpost'


class CashFlowEntryForm(forms.ModelForm):
    class Meta:
        model = CashFlowEntry
        fields = ('created_at', 'status', 'operation_type', 'category', 'subcategory', 'amount', 'comment')
        widgets = {
            'created_at': DateInput(),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Необязательный комментарий'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = Status.objects.order_by('name')
        self.fields['operation_type'].queryset = OperationType.objects.order_by('name')
        self.fields['category'].queryset = Category.objects.select_related('operation_type').order_by(
            'operation_type__name',
            'name',
        )
        self.fields['subcategory'].queryset = Subcategory.objects.select_related(
            'category',
            'category__operation_type',
        ).order_by('category__name', 'name')
        self.fields['comment'].required = False
        style_form(self)
        self._apply_related_querysets()

    def _apply_related_querysets(self):
        operation_type_id = self.data.get('operation_type') or getattr(self.instance, 'operation_type_id', None)
        category_id = self.data.get('category') or getattr(self.instance, 'category_id', None)

        if operation_type_id:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(
                operation_type_id=operation_type_id,
            )

        if category_id:
            self.fields['subcategory'].queryset = self.fields['subcategory'].queryset.filter(
                category_id=category_id,
            )


class CashFlowFilterForm(forms.Form):
    created_from = forms.DateField(label='С даты', required=False, widget=DateInput())
    created_to = forms.DateField(label='По дату', required=False, widget=DateInput())
    status = forms.ModelChoiceField(label='Статус', queryset=Status.objects.none(), required=False)
    operation_type = forms.ModelChoiceField(
        label='Тип',
        queryset=OperationType.objects.none(),
        required=False,
    )
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.none(), required=False)
    subcategory = forms.ModelChoiceField(
        label='Подкатегория',
        queryset=Subcategory.objects.none(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = Status.objects.order_by('name')
        self.fields['operation_type'].queryset = OperationType.objects.order_by('name')
        self.fields['category'].queryset = Category.objects.select_related('operation_type').order_by(
            'operation_type__name',
            'name',
        )
        self.fields['subcategory'].queryset = Subcategory.objects.select_related('category').order_by(
            'category__name',
            'name',
        )
        style_form(self)
        self._apply_related_querysets()

    def _apply_related_querysets(self):
        operation_type_id = self.data.get('operation_type')
        category_id = self.data.get('category')

        if operation_type_id:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(
                operation_type_id=operation_type_id,
            )

        if category_id:
            self.fields['subcategory'].queryset = self.fields['subcategory'].queryset.filter(
                category_id=category_id,
            )

    def clean(self):
        cleaned_data = super().clean()
        created_from = cleaned_data.get('created_from')
        created_to = cleaned_data.get('created_to')

        if created_from and created_to and created_from > created_to:
            self.add_error('created_to', 'Дата окончания должна быть не раньше даты начала.')

        return cleaned_data

    def filter_queryset(self, queryset):
        if not self.is_valid():
            return queryset

        data = self.cleaned_data

        if data['created_from']:
            queryset = queryset.filter(created_at__gte=data['created_from'])
        if data['created_to']:
            queryset = queryset.filter(created_at__lte=data['created_to'])
        if data['status']:
            queryset = queryset.filter(status=data['status'])
        if data['operation_type']:
            queryset = queryset.filter(operation_type=data['operation_type'])
        if data['category']:
            queryset = queryset.filter(category=data['category'])
        if data['subcategory']:
            queryset = queryset.filter(subcategory=data['subcategory'])

        return queryset
