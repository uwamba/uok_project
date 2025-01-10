from django import template

register = template.Library()

@register.filter
def dict_item(dictionary, key):
    """Fetch the selected option ids for the given question id."""
    if not dictionary:
        return []
    # Return a list of selected option ids for the given question id
    selected_option_ids = [detail.selected_option_id for detail in dictionary if detail.question_id == key]
    return selected_option_ids


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})