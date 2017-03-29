#!/usr/bin/python
# -*- coding: utf-8 -*-
from dongshuo import Connector
from  dongshuo_matrial_import  import Connector_material
from  dongshuo_supplier_import import Connector_supplier
from  dongshuo_customer_import import Connector_customer
from  dongshuo_employee_import import Connector_employee

#    material
#connector_m = Connector_material()
#connector_m.dongshuo2odoo_material(limit, 'update')
#    supplier
#connector_s = Connector_supplier()
#connector_s.dongshuo2odoo_supplier(limit,'update')
#connector_s.dongshuo2odoo_supplier_linkman(limit)
#connector_s.dongshuo2odoo_supplier_bank(limit)

ARG = { 
    'odoo_user':'admin',
    'odoo_passwd':'admin',
    'odoo_dbname':'csodoo',
    'odoo_server':'192.168.10.191',
    'odoo_protocol':'xmlrpc',
    'odoo_port':8059,

    'dongshuo_server':'192.168.10.2',
    'dongshuo_user':'sa',
    'dongshuo_password':'719799',
    'dongshuo_database': 'mtlerp-running',
}

def importor(arg=None, limit=1, model='create', obj_list=['material', 'supplier', 'supplier_linkman','supplier_bank'],):
    for obj in obj_list:
        if obj == 'material':
            connector_m = Connector_material(ARG)
            connector_m.dongshuo2odoo_material(limit, model)
        elif obj == 'supplier':
            connector_s = Connector_supplier(ARG)
            connector_s.dongshuo2odoo_supplier(limit,model)
        elif obj == 'supplier_linkman':
            connector_s = Connector_supplier(ARG)
            connector_s.connector_s.dongshuo2odoo_spplier_linkman(limit,model)
        elif obj == 'supplier_bank':
            connector_s = Connector_supplier(ARG)
            connector_s.dongshuo2odoo_supplier_bank(limit,model)
        elif obj == 'customer':
            connector_s = Connector_customer(ARG)
            connector_s.dongshuo2odoo_customer(limit,model)
        elif obj == 'customer_linkman':
            connector_s = Connector_customer(ARG)
            connector_s.dongshuo2odoo_customer_linkman(limit,model)
        elif obj == 'employee':
            connector_s = Connector_employee(ARG)
            connector_s.dongshuo2odoo_employee(limit,model)


importor(ARG, 50, 'create', ['customer',],)
print "__end__"
