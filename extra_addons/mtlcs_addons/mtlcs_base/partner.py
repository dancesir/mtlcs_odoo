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
from lxml import etree

Supplier_State = [('draft', u'草稿'), ('w_account', u'待财务'), ('w_technical', u'工艺'), ('w_general_manager', u'待总经理'), ('done', u'完成'),
                  ('cancel', u'取消')]
Customer_State = [('draft', u'草稿'), ('w_director', u'待主管'), ('w_chief_inspector', u'待总监'), ('done', u'完成')]


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _default_active(self, cr, uid, context=None):
        return False

    _columns = {
        'dongshuo_id': fields.integer('DongShuo ID'),
        'dongshuo_code': fields.char('DongShuo code', size=32),
        'state': fields.selection(Supplier_State, 'State'),
        'cus_state': fields.selection(Customer_State, 'State'),
        'strict_supplier': fields.boolean(u'需要评审'),
        'supplier_type': fields.selection([('a', u'A类'), ('b', u'B类'), ('c', u'C类'), ('w', u'外包类'), ('f', '服务类'), ('j', '机修类')], u'供应商分类'),
        # supplier field
        "is_tax_varify": fields.boolean(u'税务登记书'),
        "is_business_license": fields.boolean(u'营业执照'),
        "is_cooperation": fields.boolean(u'合作协议'),
        "is_environment": fields.boolean(u'环保协议'),
        "is_quality": fields.boolean(u'品质协议'),
        "need_trial": fields.boolean(u'需要试用'),

        #################  field for customer  #############################
        'short_name': fields.char(u'简称', size=32),
        'en_name': fields.char(u'英文名称', size=32),
        'registered_capital': fields.integer(u'注册资金'),
        'credit_code': fields.char(u'机构信用代码', size=16),
        # 经营范围  do it by tags
        # 行业类别  do it by tags
        # 企业性质  do it by tags
        'turnover': fields.integer(u'营业额'),
        'year_purchase_amount': fields.integer(u'PCB采购额'),
        'employee_count': fields.integer(u'公司人数'),
        'payment_type': fields.selection([('bank',u'转账'),('cash',u'现金')], u'付款方式'),
        'production_company_id': fields.many2one('res.partner', u'投产限制地'),
        'type': fields.selection([
            ('default', 'Default'),
            ('invoice', 'Invoice'),
            ('delivery', 'Shipping'),
            ('technical', u'技术'),
            ('business', u'商务'),
            ('contact', 'Contact'),
            ('other', 'Other')],
            u'联系类型',),

        'contact_name': fields.char(u'联系人', size=32),
    }

    _defaults = {
        'active': lambda self, cr, uid, ctx: self._default_active(cr, uid, context=ctx),
        'state': 'draft',
        'cus_state': 'draft',
        'strict_supplier': True,
    }
    # Supplier wkf

    # ==========20170223修改res.partner的write方法
    def write(self, cr, uid, ids, vals, context=None):
        # res.partner must only allow to set the company_id of a partner if it
        # is the same as the company of all users that inherit from this partner
        # (this is to allow the code from res_users to write to the partner!) or
        # if setting the company_id to False (this is compatible with any user
        # company)
        # 修改合作伙伴下创建新联系人为默认有效，已审核状态
        if vals.get('child_ids'):
            for val in vals.get('child_ids'):
                if val[2]:
                    val[2].update({
                        'active': True,
                        'state': 'done',
                        'supplier': False,
                        'customer': False,
                    })
        result = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return result

    # ==========20170223修改res.partner的create方法
    def create(self, cr, uid, vals, context=None):
        # 修改合作伙伴下创建新联系人默认为有效，已审核状态
        if vals.get('child_ids'):
            for val in vals.get('child_ids'):
                if val[2]:
                    val[2].update({
                        'active': True,
                        'state': 'done',
                        'supplier': False,
                        'customer': False,
                    })
        partner = super(res_partner, self).create(cr, uid, vals, context=context)
        return partner

    # ==========20170223修改合作伙伴联系人的显示方式（不显示公司名）
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(res_partner, self).name_get(cr, uid, ids, context=context)

        del_res = []
        add_res = []
        for record in self.browse(cr, uid, ids, context=context):
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, record.name)
                del_res.append((record.id, name))
                add_res.append((record.id, record.name))
        if len(del_res):
            for del_re in del_res:
                res.remove(del_re)
            res.extend(add_res)

        return res

    def confirm(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'w_account'}, context=context)
        return True

    def account_approve(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'w_technical'}, context=context)
        return True

    def technical_approve(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'state': 'w_general_manager'}, context=context)
        return True

    def general_manager_approve(self, cr, uid, ids, context=None, ):
        return self.action_done(cr, uid, ids, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0], {'state': 'draft', 'active': False}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        ref_supplier = self._compute_ref_supplier(cr, uid, ids, context=context)
        self.write(cr, uid, ids[0], {'state': 'done', 'active': True, 'ref_supplier': ref_supplier}, context=context)
        return True

    def _compute_ref_supplier(self, cr, uid, ids, context=None):
        supplier = self.browse(cr, uid, ids[0], context=context)
        ref = self.pool.get('ir.sequence').get(cr, uid, 'ref.supplier.%s' % supplier.supplier_type)
        return ref

    # Customer wkf
    def cus_confirm(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'cus_state': 'w_director'}, context=context)
        return True

    def cus_director_approve(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'cus_state': 'w_chief_inspector'}, context=context)
        return True

    def cus_chief_inspector_approve(self, cr, uid, ids, context=None):
        self.cus_action_done(cr, uid, ids, context=context)
        return True

    def cus_action_draft(self, cr, uid, ids, context=None, ):
        self.write(cr, uid, ids[0], {'cus_state': 'draft', 'active': False}, context=context)
        return True

    def cus_action_done(self, cr, uid, ids, context=None):
        data = {
            'cus_state': 'done',
            'active': True,
            'ref_customer': self.pool.get('ir.sequence').get(cr, uid, 'ref.customer'),
        }
        return self.write(cr, uid, ids[0], data, context=context)






    #customer wkf
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
