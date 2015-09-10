from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as _ARAV
from bika.lims.browser.analysisrequest import AnalysisRequestsView as _ARV
from bika.lims.permissions import *
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class AnalysisRequestsView(_ARV, _ARAV):
    ar_add = ViewPageTemplateFile("../analysisrequest/templates/ar_add.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.catalog = "portal_catalog"

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, 'portal_catalog')
        import pdb;pdb.set_trace()
        if 'SamplingRoundUID' not in contentFilter.keys():
            contentFilter['SamplingRoundUID'] = self.context.UID()
        return bc(contentFilter)

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # We give the number of analysis request templates in order to fill out the analysis request form
            # automatically :)
            num_art = len(self.context.ar_templates)
            self.context_actions[self.context.translate(_('Add new'))] = {
                'url': self.context.aq_parent.absolute_url() + \
                    "/portal_factory/"
                    "AnalysisRequest/Request new analyses/ar_add?samplinground="
                    + self.context.UID() + "&ar_count=" + str(num_art),
                'icon': '++resource++bika.lims.images/add.png'}
        return super(AnalysisRequestsView, self).__call__()
