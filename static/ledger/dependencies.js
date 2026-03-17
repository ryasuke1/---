(function () {
    function text(value) {
        return value === null || value === undefined ? "" : String(value);
    }

    function readData(id) {
        var node = document.getElementById(id);
        if (!node) {
            return [];
        }
        return JSON.parse(node.textContent);
    }

    function renderOptions(select, items, selectedValue, placeholder) {
        var current = text(selectedValue);
        select.innerHTML = "";

        if (placeholder !== undefined) {
            var emptyOption = document.createElement("option");
            emptyOption.value = "";
            emptyOption.textContent = placeholder;
            select.appendChild(emptyOption);
        }

        items.forEach(function (item) {
            var option = document.createElement("option");
            option.value = item.id;
            option.textContent = item.name;
            if (text(item.id) === current) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        if (current && !items.some(function (item) { return text(item.id) === current; })) {
            select.value = "";
        }
    }

    window.setupLedgerDependencies = function setupLedgerDependencies(config) {
        var typeSelect = config.typeSelectId ? document.getElementById(config.typeSelectId) : null;
        var categorySelect = document.getElementById(config.categorySelectId);
        var subcategorySelect = document.getElementById(config.subcategorySelectId);

        if (!categorySelect || !subcategorySelect) {
            return;
        }

        var categories = readData(config.categoriesDataId);
        var subcategories = readData(config.subcategoriesDataId);
        var placeholders = config.placeholderText || {};

        function syncCategories(preserveValue) {
            var selectedType = typeSelect ? text(typeSelect.value) : "";
            var currentValue = preserveValue ? categorySelect.value : "";
            var filtered = selectedType
                ? categories.filter(function (item) {
                    return text(item.operation_type_id) === selectedType;
                })
                : categories;

            renderOptions(categorySelect, filtered, currentValue, placeholders.category);
            categorySelect.disabled = filtered.length === 0;
        }

        function syncSubcategories(preserveValue) {
            var selectedCategory = text(categorySelect.value);
            var currentValue = preserveValue ? subcategorySelect.value : "";
            var filtered = selectedCategory
                ? subcategories.filter(function (item) {
                    return text(item.category_id) === selectedCategory;
                })
                : subcategories;

            renderOptions(subcategorySelect, filtered, currentValue, placeholders.subcategory);
            subcategorySelect.disabled = config.requireCategoryForSubcategory ? !selectedCategory : filtered.length === 0;
        }

        if (typeSelect) {
            typeSelect.addEventListener("change", function () {
                syncCategories(false);
                syncSubcategories(false);
            });
        }

        categorySelect.addEventListener("change", function () {
            syncSubcategories(false);
        });

        syncCategories(true);
        syncSubcategories(true);
    };
}());
