#!/usr/bin/python
# -*- coding: utf-8 -*-
from dongshuo import Connector


class Connector_supplier(Connector):
    #供应商的分类编码  2002供应商业   2004外协  2005机修供应商
    _SQL_Supplier ='SELECT top %s *FROM TBCustmer WHERE  (CustmerClass = \'2002\') or (CustmerClass = \'2004\') or (CustmerClass = \'2005\')'

    def dongshuo2odoo_supplier_bank(self, limit=1, model='create'):
        odoo = self.odoo
        dongshuo = self.dongshuo
        for row in self.dongshuo_query(Connector_supplier._SQL_Supplier % limit):
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


    def dongshuo2odoo_supplier_linkman(self, limit=1, model='create'):
        odoo = self.odoo
        dongshuo = self.dongshuo
        for row in self.dongshuo_query(Connector_supplier._SQL_Supplier % limit):
            col = self.Diction_Row(row)
            # for i in col:
            #    print i, col[i]

            # link_man  linkman linkmobil linktel
            link_man = col['linkman']
            link_man = "".join(link_man.split())

            if link_man:
                link_man_data = {
                    'name': col['linkman'],
                    'phone': col['linktel'],
                    'mobile': col['linkmobil'],
                    'supplier': False,
                    'customer': False,
                    'active': True,
                }
                # linkman 是否已存在
                supplier_ids = odoo.execute('res.partner', 'search', [('dongshuo_id', '=', col['id'])])
                supplier_id = supplier_ids and supplier_ids[0] or None
                if supplier_id:
                    link_man_data.update({'parent_id': supplier_id})
                    link_man_ids = odoo.execute('res.partner', 'search',
                                                [('parent_id', '=', supplier_id), ('name', '=', link_man)])
                    link_man_id = link_man_ids and link_man_ids[0] or None
                    if not link_man_id:
                        link_man_id = odoo.execute('res.partner', 'create', link_man_data)
                        print "create link_man %s %s for supplier_id %s  " % (link_man, link_man_id, supplier_id)
                    else:
                        print u"link_man %s ID:%s 已经存在" % (link_man, link_man_id)
                else:
                    print u"未找到对应的供应商"
            else:
                print u"没有联系人信息"

    def dongshuo2odoo_supplier(self, limit=1, model='create', ):
        odoo = self.odoo
        dongshuo = self.dongshuo

        for row in self.dongshuo_query(Connector_supplier._SQL_Supplier % limit):

            col = self.Diction_Row(row)
            name = col['custmertname'] or col['custmername']
            ref_supplier = col['custmercode']
            dongshuo_id = col['id']

            if not ref_supplier:
                print "not find supplier code"

            # for i in col:
            #    print i, col[i]

            data = {
                'dongshuo_id': dongshuo_id,
                'name': name,
                'ref_supplier': ref_supplier,

                'state_id': None,
                'city': None,
                'street': col['registaddr'],
                'zip': col['zipcode'],

                'website': None,
                'phone': col['linktel'],
                'mobile': None,
                'fax': col['faxcode'],
                'email': None,
                'is_company': True,
                'comment': col['memo'],
                'user_id': None,
                'active': True,
                'supplier': True,
                'customer': False,
                'create_date': col['createdate'],
            }
            # print data

            # 确定ODOO是否已经存在，没有则创建
            supplier_ids = odoo.execute('res.partner', 'search', [('dongshuo_id', '=', dongshuo_id)])
            if supplier_ids:
                print u"供应商 %s %s odoo_id:%s 已经存在" % (ref_supplier, name, supplier_ids)
                if model == 'update':
                    res = odoo.execute('res.partner', 'write', supplier_ids[0], data)
                    print "update material %s" % (res)
            else:
                # TODO: 创建联系人， 银行帐号， 物料供应信息等 复杂字段
                # TODO: 检查必须字段
                supplier_id = odoo.execute('res.partner', 'create', data)
                if supplier_id:
                    print "create suppliser %s %s %s " % (supplier_id, ref_supplier, name)



















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
