#!/usr/bin/python
# -*- coding: utf-8 -*-
from dongshuo import Connector, DongShuo


class Connector_customer(Connector):

    _SQL_Customer ='SELECT top %s *FROM TBCustmer WHERE  (CustmerClass = \'2001\') order by id'

    def dongshuo2odoo_customer_bank(self, limit=1, model='create'):
        odoo = self.odoo
        dongshuo = self.dongshuo
        for row in self.dongshuo_query(Connector_customer._SQL_Customer % limit):
            col = self.Diction_Row(row)
            #for i in col:
            #    if 'bank' in i:
            #        print i, col[i]
            supplier_ids = odoo.execute('res.partner', 'search', [('dongshuo_id', '=', col['id'])])
            supplier_id = supplier_ids and supplier_ids[0] or None
            if supplier_id:
                bankname = col['bankname']
                bankcode = col['bankcode']
                if bankname and bankcode:
                    bank_ids = odoo.execute('res.partner.bank', 'search',  [('partner_id', '=', supplier_id), ('acc_number', '=', bankcode)])
                    bank_id = bank_ids and bank_ids[0] or None
                    if not bank_id:
                        bank_id = odoo.execute('res.partner.bank', 'create', {
                            'partner_id': supplier_id,
                            'acc_number': bankcode,
                            'bank_name': bankname,
                            'state': 'bank',
                        })
                        print "create bank%s:ID%s for supplierID%s" % (bankcode, bank_id, supplier_id)
                    else:
                        print "bank has exist, not need import"
                else:
                    print "not found bank info"
            else:
                print "Supplier not found"

    def dongshuo2odoo_customer_linkman(self, limit=1, model='create'):
        odoo = self.odoo
        dongshuo = self.dongshuo

        arg = self.arg
        dongshuo_server = arg.get('dongshuo_server','192.168.10.2')
        dongshuo_user = arg.get('dongshuo_user','sa')
        dongshuo_password = arg.get('dongshuo_password','719799')
        dongshuo_database = arg.get('dongshuo_database','mtlerp-running')
        conn2= DongShuo(dongshuo_server, dongshuo_user, dongshuo_password, dongshuo_database)

        for row in self.dongshuo_query(Connector_customer._SQL_Customer % limit):
            col = self.Diction_Row(row)
            dongshuo_id = col['id']
            print "dongshuo2odoo_customer %s" % dongshuo_id
            #for i in col:
            #    print i, col[i]
            # customer_id 是否已存在
            customer_ids = odoo.execute('res.partner', 'search', [('dongshuo_id', '=', dongshuo_id)])
            customer_id = customer_ids and customer_ids[0] or None
            if not customer_id:
                print "Not found customer_ids in odoo"
                continue

            conn2.execute_query('SELECT * FROM TCCustmerLinkman WHERE CustmerCode=%s order by isdefault desc', col['custmercode'])
            for linkman_row in conn2:
                linkman_col = self.Diction_Row(linkman_row)
                linkman_name = linkman_col['linkmanname']

                #print linkman_col
                linkman_data = {
                    'parent_id':customer_id,
                    'name':linkman_name,
                    'state_id': None,
                    'city': None,
                    'street': linkman_col['sendaddr'],
                    'phone': linkman_col['linktel'],
                    'mobile': linkman_col['linkmobil'],
                    'fax': linkman_col['faxcode'],
                    'email': None,
                    'is_company': False,
                    'user_id': None,
                    'active': True,
                    'supplier': False,
                    'customer': False,
                    'type': 'contact',
                }
                link_ids =  odoo.execute('res.partner', 'search', [('parent_id', '=', customer_id), ('name', 'like', linkman_name)])
                if not link_ids:
                    link_id = odoo.execute('res.partner', 'create', linkman_data)
                    print "create link_id %s %s for customer_id %s  " % (linkman_name, linkman_data, link_id)
                else:
                    print u"delivery_ids %s ID:%s 已经存在" % (linkman_name, link_ids)



            # #添加默认发货地址
            # if col['deladdr']:
            #     name = col['linkman'] or col['deladdr']
            #     delivery_data = {
            #         'parent_id':customer_id,
            #         'name': name,
            #         'state_id': None,
            #         'city': None,
            #         'street': col['deladdr'],
            #         'phone': col['linktel'],
            #         'mobile': col['linkmobil'],
            #         'fax': col['faxcode'],
            #         'email': None,
            #         'is_company': False,
            #         'user_id': None,
            #         'active': True,
            #         'supplier': False,
            #         'customer': False,
            #         'type': 'delivery',
            #     }
            #     delivery_ids =  odoo.execute('res.partner', 'search', [('parent_id', '=', customer_id), ('name', 'like', name)])
            #     if not delivery_ids:
            #         delivery_id = odoo.execute('res.partner', 'create', delivery_data)
            #         print "create delivery_id %s %s for customer_id %s  " % (name, delivery_data, customer_id)
            #     else:
            #         print u"delivery_ids %s ID:%s 已经存在" % (name, delivery_ids)


















    def dongshuo2odoo_customer(self, limit=1, model='create', ):
        odoo = self.odoo
        dongshuo = self.dongshuo

        for row in self.dongshuo_query(Connector_customer._SQL_Customer % limit):
            col = self.Diction_Row(row)
            dongshuo_id = col['id']

            print "dongshuo2odoo_customer %s" % dongshuo_id

            name = col['custmertname'] or col['custmername']
            ref_customer = col['custmercode']


            if not ref_customer:
                print "not find supplier code"
                continue
            data = {
                'dongshuo_id': dongshuo_id,
                'name': name,
                'ref_customer': ref_customer,

                'state_id': None,
                'city': None,
                'street': col['registaddr'],
                'zip': col['zipcode'],

                'website': None,
                'phone': col['linktel'],
                'mobile': col['linkmobil'],
                'fax': col['faxcode'],
                'email': col['emailcode'],
                'is_company': True,
                'comment': col['memo'],
                'user_id': None,
                'active': True,
                'supplier': False,
                'customer': True,
                'create_date': col['createdate'],
            }
            # print data

            # 确定ODOO是否已经存在，没有则创建
            costomer_ids = odoo.execute('res.partner', 'search', [('dongshuo_id', '=', dongshuo_id)])
            if costomer_ids:
                print u"客户 %s %s odoo_id:%s 已经存在" % (ref_customer, name, costomer_ids)
                if model == 'update':
                    res = odoo.execute('res.partner', 'write', costomer_ids[0], data)
                    print "update material %s" % (res)
            else:
                # TODO: 创建联系人， 银行帐号， 物料供应信息等 复杂字段
                # TODO: 检查必须字段
                costomer_id = odoo.execute('res.partner', 'create', data)
                if costomer_id:
                    print "create suppliser %s %s %s " % (costomer_id, ref_customer, name)



















#




















# ===============================================================================
# conn = _mssql.connect(server='192.168.10.2', user='sa', password='719799',database='mtlerp-running',charset='utf8') 
# 
# 
# 
# conn.execute_query(sql )   
# i = 0    
# for row in conn:
#    txt = row[4]
#    
#    print txt,type(txt), txt.encode('gbk')
# 
#    i+=1
#    if i >10:
#        break
# ===============================================================================
