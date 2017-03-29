#!/usr/bin/python
# -*- coding: utf-8 -*-
from  dongshuo import ODOO
odoo = ODOO('admin', 'admin', 'odoo',)

import xlrd
work = xlrd.open_workbook('material_categ.xls')
sheet = work.sheet_by_index(0)
num_row = sheet.nrows

for i in range(num_row):
    c_code = sheet.row(i)[4].value
    name = sheet.row(i)[7].value
    dot = r'.'
    parent_c_code = None
    code = None
    if dot in c_code:
        parent_c_code = c_code[0:c_code.rfind(dot)]
        code = c_code[c_code.rfind(dot)+1:]
    else:
        code = c_code
    print i, name,  c_code,    parent_c_code, code
    model = 'product.category'

    #
    ids = odoo.search(model,[('complete_code','=',c_code)])
    if not ids:

        data = {'name':name, 'code':code}

        if parent_c_code:
            parent_ids = odoo.search(model,[('complete_code','=',parent_c_code)],limit=1)
            parent_id = parent_ids and parent_ids[0]
            if parent_id:
               data.update({'parent_id': parent_id})
            else:
                print "not found parent_id"
                continue

        new_id = odoo.create(model, data)

        print 'new category',new_id














