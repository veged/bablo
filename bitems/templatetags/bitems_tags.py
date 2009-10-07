from django.template import Library

register = Library()

@register.inclusion_tag('bitem')
def bitem(bitem, current_action=None, cbitem=False):
    return locals()

@register.inclusion_tag('bitems_short')
def bitems_short(bitems, title, name, cbitem=False):
    context = locals()
    context['bitems'] = bitems[:10]
    context['bitems_count'] = bitems.count()
    context['bitems_has_more'] = context['bitems_count'] > 10
    return context

@register.inclusion_tag('bitems_middle')
def bitems_middle(bitems, title, name, cbitem=False, skip=0, bitem_action=False, blist_action=False):
    context = locals()

    context['more_url'] = "/bitems/"
    if cbitem:
        context['more_url'] += "%s/" % cbitem.id
    if bitem_action and bitem_action != name:
        context['more_url'] += "%s/" % bitem_action
    context['more_url'] += "%s/" % name

    context['bitems'] = bitems[skip:skip+10]
    context['bitems_remainder'] = max([bitems.count() - (skip + 10), 0])
    context['bitems_more'] = min([context['bitems_remainder'], 10])
    context['bitems_more_skip'] = skip + 10
    context['bitems_less'] = min([10, skip])
    context['bitems_less_skip'] = skip - 10
    return context

@register.inclusion_tag('bitem_form')
def bitem_form(bitem, form, action=None):
    return locals()

@register.inclusion_tag('bitem_actions')
def bitem_actions(bitem, current_action=None, cbitem=False):
    return locals()

@register.inclusion_tag('bitem_action')
def bitem_action(bitem, action_name, action_title, current_action=None, cbitem=False):
    context = locals()
    context['action_active'] = action_name == current_action and not(cbitem)
    if cbitem:
        context['action_url'] = "/bitems/%s/%s/%s/" % (cbitem.id, action_name, bitem.id)
    else:
        context['action_url'] = "/bitems/%s/%s/" % (bitem.id, action_name)
    return context
