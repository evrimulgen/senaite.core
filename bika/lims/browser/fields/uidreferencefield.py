# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.Field import ObjectField, Field
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims import logger
from bika.lims.interfaces.field import IUIDReferenceField
from plone.api.portal import get_tool
from zope.interface import implements


class ReferenceException(Exception):
    pass


def is_uid(value):
    """Checks that the string passed is a valid UID of an existing object
    """
    uc = get_tool('uid_catalog')
    brains = uc(UID=value)
    return brains and True or False


def is_brain(brain_or_object):
    """Checks if the passed in object is a portal catalog brain
    """
    return ICatalogBrain.providedBy(brain_or_object)


def is_at_content(brain_or_object):
    """Checks if the passed in object is an AT content type
    """
    return isinstance(brain_or_object, BaseObject)


class UIDReferenceField(ObjectField):
    """A field that stores References as UID values.
    """
    _properties = Field._properties.copy()
    _properties.update({
        'type': 'uidreference',
        'default': '',
        'default_content_type': 'text/plain',
    })

    implements(IUIDReferenceField)

    security = ClassSecurityInfo()

    @security.private
    def get_object(self, instance, value):
        """Resolve a UID to an object.
        """
        if not value:
            return None
        elif is_at_content(value):
            return value
        else:
            uc = get_tool('uid_catalog')
            brains = uc(UID=value)
            if brains:
                return brains[0].getObject()
            logger.error("%s.%s: Resolving UIDReference failed for %s (drop)" %
                         instance, self.getName(), value)

    @security.private
    def get_uid(self, instance, value):
        """Takes a brain or object (or UID), and returns a UID.
        """
        if not value:
            ret = ''
        elif is_brain(value):
            ret = value.UID
        elif is_at_content(value):
            ret = value.UID()
        elif is_uid(value):
            ret = value
        else:
            raise ReferenceException("%s.%s: Cannot resolve UID for %s" %
                                     (instance, self.getName(), value))
        return ret

    @security.private
    def get(self, instance, **kwargs):
        """Grab the stored value, and resolve object(s) from UID catalog.
        """
        value = ObjectField.get(self, instance, **kwargs)
        if self.multiValued:
            ret = filter(
                lambda x: x, [self.get_object(instance, uid) for uid in value])
        else:
            ret = self.get_object(instance, value)
        return ret

    @security.private
    def set(self, instance, value, **kwargs):
        """Accepts a UID, brain, or an object (or a list of any of these),
        and stores a UID or list of UIDS.
        """
        if self.multiValued:
            if type(value) not in (list, tuple):
                value = [value, ]
            ret = [self.get_uid(instance, val) for val in value]
        else:
            ret = self.get_uid(instance, value)
        ObjectField.set(self, instance, ret, **kwargs)
