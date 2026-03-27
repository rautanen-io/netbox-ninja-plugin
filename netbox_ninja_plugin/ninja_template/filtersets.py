from django.db.models import Q
from django.db.models.query import QuerySet
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)


class NinjaTemplateFilterSet(NetBoxModelFilterSet):

    object_types = MultiValueCharFilter(
        method="filter_by_key",
        field_name="object_types__in",
    )

    output_type = MultiValueCharFilter(
        method="filter_by_key",
        field_name="output_type__in",
    )
    object_type_filters = MultiValueCharFilter(
        method="filter_by_key",
        field_name="object_type_filters__in",
    )
    string_filters = MultiValueCharFilter(
        method="filter_by_key",
        field_name="string_filters__in",
    )

    def search(self, queryset: QuerySet, _, value: str) -> QuerySet:
        return queryset.filter(Q(name__icontains=value) | Q(code__icontains=value))

    def filter_by_key(
        self, queryset: QuerySet, field: str, object_ids: list[int]
    ) -> QuerySet[NinjaTemplate]:
        return queryset.filter(**{f"{field}": object_ids})

    class Meta:
        model = NinjaTemplate
        fields = [
            "name",
            "object_types",
            "object_type_filters",
            "string_filters",
            "output_type",
            "code",
        ]


class NinjaTemplateStringFilterFilterSet(NetBoxModelFilterSet):
    name = MultiValueCharFilter(
        method="filter_by_key",
        field_name="name__in",
    )
    key = MultiValueCharFilter(
        method="filter_by_key",
        field_name="key__in",
    )

    def search(self, queryset: QuerySet, _, value: str) -> QuerySet:
        return queryset.filter(Q(name__icontains=value) | Q(key__icontains=value))

    def filter_by_key(
        self, queryset: QuerySet, field: str, values: list[str]
    ) -> QuerySet[NinjaTemplateStringFilter]:
        return queryset.filter(**{f"{field}": values})

    class Meta:
        model = NinjaTemplateStringFilter
        fields = [
            "name",
            "key",
        ]


class NinjaTemplateStringFilterOptionFilterSet(NetBoxModelFilterSet):
    value = MultiValueCharFilter(
        method="filter_by_key",
        field_name="value__in",
    )
    label = MultiValueCharFilter(
        method="filter_by_key",
        field_name="label__in",
    )
    string_filter = MultiValueCharFilter(
        method="filter_by_key",
        field_name="string_filter__in",
    )

    def search(self, queryset: QuerySet, _, value: str) -> QuerySet:
        return queryset.filter(
            Q(value__icontains=value)
            | Q(label__icontains=value)
            | Q(string_filter__name__icontains=value)
        )

    def filter_by_key(
        self, queryset: QuerySet, field: str, values: list[str]
    ) -> QuerySet[NinjaTemplateStringFilterOption]:
        return queryset.filter(**{f"{field}": values})

    class Meta:
        model = NinjaTemplateStringFilterOption
        fields = [
            "string_filter",
            "value",
            "label",
        ]
