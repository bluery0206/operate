from django import template
from ..utils import get_full_name

register = template.Library()

@register.filter
def full_name(profile:object, m_initial:bool=True):
	return get_full_name(profile, m_initial)


@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

