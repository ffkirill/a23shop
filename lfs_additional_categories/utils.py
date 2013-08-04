from models import AdditionalCategory


def get_filtered_products_for_additional_filter(all_products,
                                                additional_filter):
    try:
        category = AdditionalCategory.objects.get(pk=additional_filter)
    except AdditionalCategory.DoesNotExist:
        return all_products

    categories = [category]
    categories.extend(category.get_all_children())

    return all_products.filter(additional_categories__in=categories)