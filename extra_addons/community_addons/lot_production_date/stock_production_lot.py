# -*- coding: utf-8 -*-
##############################################################################
import datetime
from datetime import timedelta
from datetime import datetime as DT
import openerp
from openerp.osv import osv, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    _columns = {
        'production_date': fields.datetime(u'出厂日期/生产日期', )
    }
    _defaults = {
        'production_date': fields.datetime.now(),
    }

    def create(self, cr, uid, value, context=None):
        print ">>", context
        lot_id = super(stock_production_lot, self).create(cr, uid, value, context=context)
        if context.get('res_field') and context.get('active_model') and context.get('active_id'):
            self.pool[context.get('active_model')].write(cr, uid, context.get('active_id'), {context.get('res_field'): lot_id})
        return lot_id

    def onchange_production_date(self, cr, uid, ids, production_date, product_id, context=None):
        if (not production_date) or (not product_id):
            return {}

        product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
        field_map = {
            'life_date': 'life_time',
            'use_date': 'use_time',
            'removal_date': 'removal_time',
            'alert_date': 'alert_time'
        }

        value = {}
        for lot_f, pdt_f in field_map.items():
            duration = getattr(product, pdt_f)
            value[lot_f] = duration and (DT.strptime(production_date, DTF) + timedelta(days=duration)).strftime(DTF) or False

        return {'value': value}
