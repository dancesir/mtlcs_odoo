# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from operator import itemgetter
import time

from openerp import models, api
from openerp.osv import osv, orm, fields
from openerp.tools.misc import attrgetter

# -------------------------------------------------------------------------
# Properties
# -------------------------------------------------------------------------


class ir_property(osv.osv):
    _inherit = 'ir.property'
    _description = 'Properties'


    # @api.model
    def set_multi(self, cr, uid, ids, context=None):
        """ Assign the property field `name` for the records of model `model`
            with `values` (dictionary mapping record ids to their value).
        """
        name = ''
        model = ''
        values = ''
        # super(ir_property, self).set_multi(cr, uid, name, model, values)

        def clean(value):
            return value.id if isinstance(value, models.BaseModel) else value

        if not values:
            return

        domain = self._get_domain(name, model)
        if domain is None:
            raise Exception()

        # retrieve the default value for the field
        default_value = clean(self.get(name, model))

        # retrieve the properties corresponding to the given record ids
        self._cr.execute("SELECT id FROM ir_model_fields WHERE name=%s AND model=%s", (name, model))
        field_id = self._cr.fetchone()[0]
        company_id = self.env.context.get('force_company') or self.env['res.company']._company_default_get(model, field_id)
        refs = {('%s,%s' % (model, id)): id for id in values}
        props = self.search([
            ('fields_id', '=', field_id),
            ('company_id', '=', company_id),
            ('res_id', 'in', list(refs)),
        ])

        # modify existing properties
        for prop in props:
            id = refs.pop(prop.res_id)
            value = clean(values[id])
            if value == default_value:
                prop.unlink()
            elif value != clean(prop.get_by_record(prop)):
                prop.write({'value': value})

        # create new properties for records that do not have one yet
        for ref, id in refs.iteritems():
            value = clean(values[id])
            if value != default_value:
                self.create({
                    'fields_id': field_id,
                    'company_id': company_id,
                    'res_id': ref,
                    'name': name,
                    'value': value,
                    'type': self.env[model]._fields[name].type,
                })




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
