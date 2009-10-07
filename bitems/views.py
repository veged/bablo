# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django import newforms as forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from bablo.bitems.models import *

bitems_lists_functions = {
    'mainminuses': lambda user: Bitem.main_minuses(user),
    'lonely': lambda user: user.bitem_set.filter(parents__isnull=True, children__isnull=True).order_by('-modified'),
    'recent': lambda user: user.bitem_set.all().order_by('-modified'),
}

bitems_lists_titles = {
    'mainminuses': "Основные расходы",
    'lonely': "Нуждающиеся во внимании",
    'recent': "Недавние",
}

@login_required
def bitems_lists(request, id=None, bitem_action=None, blist_action=None):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        bitem = False
    
    context = {
        'bitem': bitem,
        'bitem_action': bitem_action,
        'blist_action': blist_action,
        'balance': Bitem.balance(request.user),
        'has_bitems': request.user.bitem_set.count() != 0,
        'bitems_lists': [],
    }
    
    for k, f in bitems_lists_functions.iteritems():
        bitems = f(request.user)
        context['bitems_lists'].append({
            'name': k,
            'bitems': bitems,
            'title': bitems_lists_titles[k],
        })
    return render_to_response('bitems_lists.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def bitems_list(request, id=None, bitem_action=None, blist_action=None, skip=0):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        bitem = False

    context = {
        'bitem': bitem,
        'bitem_action': bitem_action,
        'blist_action': blist_action,
        'skip': int(skip),
        'bitems_list': bitems_lists_functions[blist_action](request.user),
        'bitems_list_title': bitems_lists_titles[blist_action],
    }
    return render_to_response('bitems_list.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def bitem(request, id=False, bitem_action=None, blist_action=None, skip=0):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        raise Http404

    context = {
        'bitem': bitem,
        'bitem_action': bitem_action,
        'blist_action': blist_action,
        'skip': int(skip),
    }
    return render_to_response('bitem.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def bitem_edit(request, id=False, bitem_action=None):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        raise Http404

    BitemForm = forms.models.form_for_instance(bitem)
    BitemForm.save = Bitem.form_save(forms.models.make_instance_save(bitem, ['title', 'amount', 'time'], 'changed'))

    if request.method == 'POST':
        form = BitemForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect("../")
    else:
        form = BitemForm(initial=request.GET)

    context = {
        'form': form,
        'bitem_action': bitem_action,
        'bitem': bitem,
    }
    return render_to_response('bitem_edit.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def bitem_link(request, id=False, target_id=False, bitem_action=None):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        raise Http404

    try:
        target_bitem = request.user.bitem_set.get(id=target_id)
    except Bitem.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        if bitem_action == 'linkspecify':
            bitem.children.add(target_bitem)
            return HttpResponseRedirect("../../")
        if bitem_action == 'linkgeneralize':
            bitem.parents.add(target_bitem)
            target_bitem.amount = max([target_bitem.amount - bitem.amount, 0])
            target_bitem.save()
            return HttpResponseRedirect("../../")

    context = {
        'bitem_action': bitem_action,
        'bitem': bitem,
        'target_bitem': target_bitem,
        'already_link': bitem == target_bitem or bitem.descendants().has_key(target_bitem.id) or target_bitem.descendants().has_key(bitem.id)
    }
    
    return render_to_response('bitem_link.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def bitem_unlink(request, id=False, target_id=False, bitem_action=None):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        raise Http404

    try:
        target_bitem = request.user.bitem_set.get(id=target_id)
    except Bitem.DoesNotExist:
        raise Http404

    if not(target_bitem in bitem.children.all()) and not(bitem in target_bitem.children.all()):
        return HttpResponseRedirect("../../")

    if request.method == 'POST':
        bitem.children.remove(target_bitem)
        target_bitem.children.remove(bitem)
        return HttpResponseRedirect("../../")

    context = {
        'bitem_action': bitem_action,
        'bitem': bitem,
        'target_bitem': target_bitem,
    }
    return render_to_response('bitem_unlink.html',
                              context,
                              context_instance=RequestContext(request))



@login_required
def bitem_delete(request, id=False, bitem_action=None):
    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        bitem.delete()
        return HttpResponseRedirect("../../")

    context = {
        'bitem_action': bitem_action,
        'bitem': bitem,
    }
    return render_to_response('bitem_delete.html',
                              context,
                              context_instance=RequestContext(request))



@login_required
def bitem_add(request, id=False, bitem_action=None):
    BitemForm = forms.models.form_for_model(Bitem)
    BitemForm.save = Bitem.form_save(forms.models.make_model_save(Bitem, ['title', 'amount', 'time'], 'created'))

    try:
        bitem = request.user.bitem_set.get(id=id)
    except Bitem.DoesNotExist:
        bitem = False
    
    if request.method == 'POST':
        form = BitemForm(request.POST)
        if form.is_valid():
            bitem = form.save(request.user, bitem_action, bitem)
            return HttpResponseRedirect("../")
    else:
        form = BitemForm(initial=request.GET)

    context = {
        'form': form,
        'bitem_action': bitem_action,
    }
    if bitem:
        context['bitem'] = bitem
    return render_to_response('bitem_add.html',
                              context,
                              context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

