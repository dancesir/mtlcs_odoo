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
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class supplier_excle_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(supplier_excle_importor, self).apply(cr, uid, ids, context=context)
        if mod == "res.partner":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            if wizard.type == 'create':
                partner_ids = self.make_partner(cr, uid, datas, context=context, strict=wizard.strict)
            elif wizard.type == 'update':
                partner_ids = self.update_partner(cr, uid, datas, context=context, strict=wizard.strict)

            return {
                'type': 'ir.actions.act_window',
                'name': u'供应商信息导入',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', partner_ids)],
            }
        else:
            return mod

    def prepare_supplier_data(self, cr, uid, row, context=None, strict=True):

        term_obj = self.pool['account.payment.term']

        data = {
            'active': True,
            'supplier': True,
            'customer': False,
            'is_company': True,
            'state': 'done',
        }

        ref_supplier = str(row['ref_supplier']).strip()
        if ref_supplier:
            data.update({'ref_supplier': ref_supplier})
        if row.get('name'):
            data.update({'name': row.get('name')})
        if row.get('contact_name'):
            data.update({'contact_name': row.get('contact_name')})
        if row.get('phone'):
            data.update({'phone': row.get('phone')})
        if row.get('fax'):
            data.update({'fax': row.get('fax')})
        if row.get('dongshuo_code'):
            data.update({'dongshuo_code': row.get('dongshuo_code')})
        if ref_supplier[0].lower() in 'abcwfj':
            data.update({'supplier_type': ref_supplier[0].lower()})
        if row.get('payment_term'):
            term_ids = term_obj.search(cr, uid, [('name', '=', row.get('payment_term'))], limit=1)
            if term_ids:
                data.update({'property_supplier_payment_term': term_ids[0]})

        return data

    # ==========20170304创建或更新联系人
    def create_update_contacts(self, cr, uid, ids, partner_obj, data, parent_id, context=None):

        contact_data = {
            'active': True,
            'supplier': False,
            'customer': False,
            'is_company': False,
            'state': 'done',
            'use_parent_address': True,
            'name': data.get('contact_name'),
            'phone':data.get('phone') and data.get('phone') or False,
            'fax': data.get('fax')and data.get('fax') or False,
        }

        contact_name = contact_data['name']
        contact_ids = partner_obj.search(cr, uid,
                                         [('parent_id', '=', parent_id), ('name', '=', contact_name)],
                                         limit=1, context=context)
        contact_id = contact_ids and contact_ids[0] or None

        if contact_id:
            partner_obj.write(cr, uid, contact_id, contact_data, context=context)
            ids.append(contact_id)
            _logger.info(u'联系人更新成功 %s ID:%s' % (contact_name, contact_id))
        else:
            contact_data.update({'parent_id': parent_id})
            contact_id = partner_obj.create(cr, uid, contact_data, context=context)
            ids.append(contact_id)
            _logger.info(u'联系人创建成功 %s ID:%s' % (contact_data['name'], contact_id))

    def update_partner(self, cr, uid, datas, context=None, strict=True):
        partner_obj = self.pool.get('res.partner')
        ids = []
        for row in datas['data']:
            _logger.info(u'update_partner %s ' % row)

            data = self.prepare_supplier_data(cr, uid, row, )
            ref_supplier = data['ref_supplier']
            partner_ids = partner_obj.search(cr, uid, [('ref_supplier', '=', ref_supplier)], limit=1, context=context)
            partner_id = partner_ids and partner_ids[0] or None

            if partner_id:
                partner_obj.write(cr, uid, partner_id, data, context=context)
                ids.append(partner_id)
                _logger.info(u'供应商更新成功 %s ID:%s' % (ref_supplier, partner_id))
                # ==========20170304
                if data.get('contact_name'):
                    self.create_update_contacts(cr, uid, ids, partner_obj, data, partner_id, context=context)
                else:
                    _logger.info(u'供应商无联系人 %s ' % ref_supplier)
            else:
                _logger.info(u'供应商编码不存在 %s ' % ref_supplier)
        return ids

    def make_partner(self, cr, uid, datas, context=None, strict=True):
        partner_obj = self.pool.get('res.partner')

        ids = []
        for row in datas['data']:
            _logger.info(u'make_partner %s ' % row)

            data = self.prepare_supplier_data(cr, uid, row, )
            ref_supplier = data['ref_supplier']

            partner_ids = partner_obj.search(cr, uid, [('ref_supplier', '=', ref_supplier)], limit=1, context=context)
            partner_id = partner_ids and partner_ids[0] or None
            if partner_id:
                _logger.info(u'供应商已经存在 %s ID:%s' % (ref_supplier, partner_id))
            else:
                if data.get('name') and data.get('ref_supplier'):
                    new_id = partner_obj.create(cr, uid, data, context=context)
                    ids.append(new_id)
                    _logger.info(u'供应商创建成功 %s ID:%s' % (ref_supplier, new_id))
                    # ==========20170304
                    if data.get('contact_name'):
                        self.create_update_contacts(cr, uid, ids, partner_obj, data, new_id, context=context)
                    else:
                        _logger.info(u'供应商无联系人 %s ' % ref_supplier)
        return ids
