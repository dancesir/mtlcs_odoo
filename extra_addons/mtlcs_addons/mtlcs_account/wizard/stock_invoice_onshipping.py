# -*- coding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning



class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"

    def _default_invoice_date(self, cr, uid, context=None):
        mod = context.get('active_model')
        mid = context.get('active_id')
        date = None
        if mod == 'stock.picking' and mid:
            #TODO: should set it by pick.type
            date = self.pool[mod].browse(cr, uid, mid).date_done[:11]
        return date

    _columns = {
        'invoice_date': fields.date('Invoice Date'),
    }

    _defaults = {
        'invoice_date' : lambda self, cr, uid, ctx: self._default_invoice_date(cr, uid, context=ctx)
    }






#################