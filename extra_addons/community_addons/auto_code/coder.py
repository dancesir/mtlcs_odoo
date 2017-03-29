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
import lxml
from lxml import etree
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.addons.base.ir.ir_model import _get_fields_type


SP = ' '
SP4 = SP*4
NL = '\n'
P='#'
P1=P+NL
P79 = '#'*79 + NL
TOPL = '# -*- encoding: utf-8 -*-' +NL
Header = TOPL + P79 + P1*3 + P79 + NL*2
End_Line = NL*3 + P79

Template_OE ='''
{
    "name": "%(module_name)s",
    "version": "1.0",
    "author": "Jon <alangwansui@qq.com>",
    "category": "",
    "description": """
            %(module_description)s
    """,
    "website": "",
    "depends": ["base", ],
    "data": [
        "xxx.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],
    "test": [
    ],
    "installable": True,
    "auto_install": False,
}
'''

class state_state(osv.osv):
    _name = 'state.group'
    _columns = {
        'name' : fields.char('Name', size=32),
        'string' :fields.char('String', size=32)
    }


class ir_model(osv.osv):
    _inherit = 'ir.model'

    def name_get(self, cr, uid, ids, context=None):
        res = super(ir_model, self).name_get(cr, uid, ids, context=context)
        if context.get('show_model'):
            new_res = []
            for i in self.read(cr, uid, [i[0] for i in res], ['model'], context=context):
                new_res.append((i['id'], i['model']))
                res = new_res
        return res


class coder_cls(osv.osv):
    _name = 'coder.coder'

    _template_uniq = SP4*2 + "('%s_uniq', 'unique(%s)', '%s must be uniq')," + NL

    _columns = {
        'name': fields.char(u"Model Name", size=32,),
        'order': fields.char('Order'),
        'inherit': fields.many2one('ir.model', 'Inherit',),
        'f_ids': fields.one2many('coder.field', 'cls_id', 'Fields'),
        'text': fields.text(u'Coder'),
        'module_name': fields.char('module name', size=32,),
        'module_description': fields.char('module description', size=32,),
    }

    def get_dict(self, coder, context=None):
        cls_name = (coder.inherit.model or coder.name).replace('.','_')
        module_name = coder.module_name and coder.module_name.title() or 'XXX XXXX',
        dict = {
            'cls_name': cls_name,
            'module_name': module_name,
            'module_description': coder.module_description or module_name,
        }
        return dict

    def write_xml(self, cr, uid, ids, context=None):
        co = self.browse(cr, uid, ids[0], context=context)
        txt = ''
        return self.write(cr, uid, ids[0], {'text': txt}, context=context)

    def str_view_search(self, cr, uid, co, context=None):
        return
    def str_view_tree(self, cr, uid, co, context=None):
        return
    def str_view_form(self, cr, uid, co, context=None):
        return
    def str_menu(self, cr, uid, co, context=None):
        return

    def write_init(self, cr, uid, ids, context=None):
        co = self.browse(cr, uid, ids[0], context=context)
        cls_name = self.get_dict(co)['cls_name']
        txt = Header[:] + 'import %s' % cls_name + End_Line
        return self.write(cr, uid, ids[0], {'text': txt}, context=context)

    def write_openerp(self, cr, uid, ids, context=None):
        co = self.browse(cr, uid, ids[0], context=context)
        txt = Header[:]
        txt += Template_OE % self.get_dict(co)
        txt += End_Line
        return self.write(cr, uid, ids[0], {'text': txt}, context=context)

    def write_py(self, cr, uid, ids, context=None):
        co = self.browse(cr, uid, ids[0], context=context)
        txt = Header[:]
        txt += self.str_pre(cr, uid, co)
        txt += self.str_columns(cr, uid, co)
        txt += self.str_defaults(cr, uid, co)
        txt += self.str_sql_constraints(cr, uid, co)
        txt += End_Line

        return self.write(cr, uid, ids[0], {'text': txt}, context=context)

    def str_pre(self, cr, uid, co):
        cls_name = (co.inherit.model or co.name).replace('.','_')
        txt = 'class %s(osv.osv):' % cls_name + NL
        if co.inherit:
            txt += SP4 + '_inherit = "%s"' % co.inherit.model + NL
        else:
            txt += SP4 + '_name = "%s"' % co.name + NL
        txt += co.order and SP4 + '_order="%s"' % co.order + NL or ''
        return txt

    def str_columns(self, cr, uid, co,):
        fields_txt = self.pool['coder.field'].make_fields(cr, uid, [], fds=co.f_ids)
        return SP4 + '_columns = {' + NL + fields_txt + SP4 + '}' + NL

    def str_defaults(self, cr, uid, co,):
        txt = SP4 + '_defaults = {' + NL + SP4 + '}' + NL
        return txt

    def str_sql_constraints(self, cr, uid, co):
        txt = SP4 + '_sql_constraints = [' + NL
        for f in co.f_ids:
            if f.uniq:
                txt += self._template_uniq % (f.name, f.name, f.name)
        txt += SP4 + ']'
        return txt


class coder_field(osv.osv):
    _name = 'coder.field'
    _order = 'sequence'
    _template = SP4*2 + "'%(name)s': fields.%(type)s(%(mode)s%(string)s%(size)s%(required)s%(readonly)s%(index)s)," + NL

    _dic_attr = {
        'type': '',
        'mode': '',
        'string': '',
        'size': '',
        'required': '',
        'readonly': '',
        'index': '',
    }

    _columns = {
        'cls_id': fields.many2one('coder.coder', u'Cls'),
        'name': fields.char(u"Name", size=32,),
        'relation': fields.many2one('ir.model', 'Relation',),
        'type': fields.selection(_get_fields_type, 'Type'),
        'str': fields.char('String', size=16),
        'size': fields.integer('Size'),
        'readonly': fields.boolean(u'Readonly'),
        'required': fields.boolean(u'Required'),
        'index': fields.boolean(u'Index'),
        'default': fields.char('Default', size=16),
        'sequence': fields.integer('Sequence'),
        'uniq': fields.boolean('Uniq'),
        #'selection': fields.many2many('state.state', 'rel_codefile_state', 'f_id', 'st_id','State'),
    }

    _defaults = {
        'type': 'char',
        'size': 16,
    }

    def onchange_name(self, cr, uid, ids, name, context=None):

        if name:
            value = {'str': name.title()}

            print value
            return {'value': value}

    def make_template_dic(self, f):
        res = self._dic_attr.copy()
        res.update({
            'name': f.name,
            'type': f.type,
            'string': '"%s", ' % f.str,
        })
        if f.type in ['man2one']:
            res.update({'mode': '"%s, "' % f.relation.model})
        if f.required:
            res.update({'required': 'required=True, '})
        if f.readonly:
            res.update({'readonly': 'readonly=True, '})
        if f.index:
            res.update({'index': 'index=True, '})
        if f.type =='char':
            res.update({'size': 'size=%s, ' % f.size})
        return res

    def make_fields(self, cr, uid, ids, fds=None, context=None):
        fds = fds or self.browse(cr, uid, ids, context=context)
        txt = ''
        for f in fds:
            txt += self._template % self.make_template_dic(f)
        return txt

########################################################################################################






