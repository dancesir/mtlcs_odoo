# -*- coding: utf-8 -*-
##############################################################################

import  oerplib

odoo = oerplib.OERP('192.168.10.191', protocol='xmlrpc', port=8059)
odoo.login('admin', '2d22', 'odoo')

msc_obj = odoo.get('material.consumption.standard')

msc_ids = msc_obj.search([('state','!=','normal')])

print len(msc_ids)

msc_obj.confirm(msc_ids[:50])
print msc_obj.general_manager_approve(msc_ids[:50])



print "__end__"