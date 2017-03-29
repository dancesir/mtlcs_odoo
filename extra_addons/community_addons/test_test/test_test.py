# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.osv.fields import _column



class test_test(osv.osv):
    _name = 'test.test'
    _columns = {
        'name': fields.char('Name', size=32),
        'code': fields.char('code', size=32),
        'code2': fields.char('code2', size=32),
        'point': fields.char('Point'),

    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'编码不能重复'),
    ]

    _defaults = {
        'point': '(0.1, 0.1)',
    }

    def cron_test(self, cr, uid, context=None):
        test_ids = self.search(cr, uid, [], context=context, limit=1)
        self.write(cr, uid, test_ids, {'name': fields.datetime.now() })
        return True

    def test(self, cr, uid, ids, context=None):
        return {
            "type": "ir.actions.act_url",
            "url": "www.baidu.com",
            "target": "self",
        }


    def set_product_category(self, cr, uid, ids, context=None):

        pdt_obj = self.pool.get('product.product')
        categ_obj = self.pool.get('product.category')
        pdt_ids = pdt_obj.search(cr, uid, [('purchase_ok','=',True),('categ_id','=',1)], context=context)
        categ_ids = categ_obj.search(cr, uid, [], context=context)
        categ_info = categ_obj.read(cr, uid, categ_ids, ['complete_code'], context=context)
        dict_categ = dict([( i['complete_code'], i['id'],) for i in categ_info])

        ok_ids = []
        for pid in pdt_ids:
            default_code = pdt_obj.read(cr, uid, pid, ['default_code'], context=context)['default_code']
            if not default_code:
                continue
            categ_code = default_code[:default_code.rfind(r'.')]
            categ_id = dict_categ.get(categ_code)

            if categ_id:
                print "OK", dict_categ.get(categ_code)
                pdt_obj.write(cr, uid, pid, {'categ_id':categ_id})
                ok_ids.append(pid)

        return {
            'domain': [('id', 'in', ok_ids)],
            'name': (u'产品分类关联'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            #'target': 'new',
        }




