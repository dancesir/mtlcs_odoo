# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _


#TODO: because of product_supplierinfo_variant,
# so need  chage product_tmpl_id to product_id

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    _columns = {
    }
    _sql_constraints = [
        ('supplier_unique', 'unique (name, product_id, company_id)',
         'The record must be unique for a product and partner on the same company!'),
    ]


class pricelist_partnerinfo(osv.osv):
    _inherit = 'pricelist.partnerinfo'
    _columns = {
        'partner_id': fields.related('suppinfo_id', 'name', domain=[('supplier', '=', True)], relation='res.partner', store=False, type='many2one', string=u'供应商', readonly=True, help="Supplier of this product"),
        'product_uom': fields.related('suppinfo_id', 'product_uom',  store=False, type='many2one', relation='product.uom', string=u"单位", readonly=True,),
        'product_tmpl_id': fields.related('suppinfo_id', 'product_tmpl_id', relation='product.template', store=False, type='many2one', string=u'产品', readonly=True,),
        'product_id': fields.related('suppinfo_id', 'product_id', relation='product.product', store=False, type='many2one', string=u'产品', readonly=True,),
        'delay': fields.related('suppinfo_id', 'delay', type='integer', string=u"交货天数"),
        # ======1115
        'name': fields.related('suppinfo_id', 'product_id', relation='product.product', store=False, type='many2one', string=u'产品', readonly=True,),
    }

    _sql_constraints = [
        ('pricelist_unique', 'unique (suppinfo_id,min_quantity)',
         'The record must be unique for Quantity, Supplier and Product!'),
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
