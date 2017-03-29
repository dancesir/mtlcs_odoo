#!/usr/bin/python
# -*- coding: utf-8 -*-
from dongshuo import Connector
import re

class Connector_material(Connector):
    def dongshuo2odoo_material(self, limit=1, model='create', ):

        odoo = self.odoo
        dongshuo = self.dongshuo
        sql = 'SELECT  top %s *   FROM   TBgoods order by id ' % limit
        # order  by  id

        for row in self.dongshuo_query(sql):
            col = self.Diction_Row(row)
            default_code = col['fgoodscodenew'] or ''
            default_code = "".join(default_code.split())
            if not default_code or not re.match('^[\d.]+$', default_code):
                print "not found default_code %s" %  default_code
                continue
            #categ_c_code =  default_code[0: default_code.rfind('.')]
            categ_id = 1#odoo.execute('product.category', 'search', [('complete_code', '=', categ_c_code)], )
            #categ_id = categ_id and categ_id[0] or 385
            #print categ_c_code, categ_id
            dongshuo_id = col['id']
            name = col['goodsname']
            product_ids = odoo.execute('product.product', 'search', ['|', ('dongshuo_id', '=', dongshuo_id),('default_code','=',default_code )] )
            # abc = col['goodsabc'] and col['goodsabc'].strip().lower() or None
            # uom_ids = odoo.execute('product.unit', 'search',  [('name','=', col['goodsunit'])])
            # uom_id = uom_ids and uom_ids[0] or None
            print "dongshuo ID %s" % dongshuo_id
            data = {
                'dongshuo_id': dongshuo_id,
                'name': name,
                'categ_id': categ_id, #
                'default_code': default_code,  ##物料编码
                'variants': col['goodsspec'],  ##型号
                'sale_ok': False,
                'purchase_ok': True,
                # 'length':
                'width': float(col['goodswidth']),
                # 'height':
                # 'abc': abc,
                # 'need_strict':
                # 'price' :float(col['goodsprice']),
                'standard_price': float(col['goodsprice']),  # purchase price
                # 'lst_price'          :None,
                # 'list_price'          :None,
                'type': 'product', #TODO
                #'supply_method': 'buy',  ## [('produce','Produce'),('buy','Buy')]
                'purchase_requisition': True,  # Bids
                # 'categ_id':
                # 'route_ids': [(0,1 rout_id)],

                # 'product_manager'    :None,
                # 'description'        :None,
                # 'description_purchase':None,
                # 'description_sale'   :None,

                'active': True,

                # 'packaging :None, ##one2many  product_packaging
                # 'rental'             :None,
                # 'state'              :None,
                'uom_id': 1,
                'uom_po_id': 1,
                'uos_id': 1,
                #                'uos_coeff'          :None,
                ###'mes_type'           :None,   ##(('fixed', 'Fixed'), ('variable', 'Variable'))
                #                'seller_delay'       :None,
                #                'seller_qty'         :None,
                #                'seller_id'          :None,
                #                'seller_ids'         :None,
                #                'loc_rack'           :None,
                #                'loc_row'            :None,
                #                'loc_case'           :None,
                #                'company_id'         :None,
            }
            # 确定ODOO是否已经存在，没有则创建
            if product_ids:
                print u"原材料 %s %s odoo_id:%s 已经存在" % (default_code, name, product_ids)
                if model == 'update':
                    try:
                        res = odoo.execute('product.product', 'write', product_ids[0], data)
                        print "update material %s" % (res)
                    except:
                         print u"程序异常1"
            else:
                try:
                    new_id = odoo.execute('product.product', 'create', data)
                    print "create material %s %s %s " % (new_id, default_code, name)
                except:
                     print u"程序异常2"






#
