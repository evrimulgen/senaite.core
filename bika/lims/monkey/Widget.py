# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.interfaces import IATWidgetVisibility
from types import DictType
from plone import api
from Acquisition import aq_base
from zope.component import getAdapters

_marker = []

# Products.Archetypes.Schema.Schemata#editableFields
def editableFields(self, instance, visible_only=False):
    """Returns a list of editable fields for the given instance
    """
    ret = []
    portal = getToolByName(instance, 'portal_url').getPortalObject()
    for field in self.fields():
        if field.writeable(instance, debug=False) and    \
               (not visible_only or
                field.widget.isVisible(
                    instance, mode='edit', field=field) != 'invisible') and \
                field.widget.testCondition(instance.aq_parent, portal, instance):
            ret.append(field)
    return ret


# Products.Archetypes.Widget.TypesWidget#isVisible
def isVisible(self, instance, mode='view', default="visible", field=None):
    """decide if a field is visible in a given mode -> 'state'.
    """
    # Emulate Products.Archetypes.Widget.TypesWidget#isVisible first
    vis_dic = getattr(aq_base(self), 'visible', _marker)
    state = default
    if vis_dic is _marker:
        return state
    if type(vis_dic) is DictType:
        state = vis_dic.get(mode, state)
    elif not vis_dic:
        state = 'invisible'
    elif vis_dic < 0:
        state = 'hidden'

    # Our custom code starts here
    if not field:
        return state

    # Look for visibility from the adapters provided by IATWidgetVisibility
    adapters = sorted(getAdapters([instance], IATWidgetVisibility),
                      key=lambda adapter: getattr(adapter[1], "sort", 1000),
                      reverse=True)
    for adapter_name, adapter in adapters:
        if field.getName() not in getattr(adapter, "field_names", []):
            # Omit those adapters that are not suitable for this field
            continue
        adapter_state = adapter(instance, mode, field, state)
        adapter_name = adapter.__class__.__name__
        logger.info("IATWidgetVisibility rule {} for {}.{} ({}): {} -> {}"
            .format(adapter_name, instance.id, field.getName(), mode, state,
                    adapter_state))
        if adapter_state == state:
            continue
        return adapter_state

    return state
