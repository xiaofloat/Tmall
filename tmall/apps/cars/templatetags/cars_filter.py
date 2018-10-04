# 注册
from django import template

register = template.Library()


@register.filter
def times(a, b):
    # print(a, b)
    return int(a) * float(b)
