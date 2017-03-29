####
import urllib, urllib2
from md5 import md5
import base64
from lxml import etree as et

def make_OrderSearchService():
    root =  et.XML('<Request service="OrderSearchService" lang="zh-CN"></Request>')
    head = et.XML('<Head>BSPdevelop</Head>')
    body = et.XML('<Body></Body>')
    OrderSearch = et.XML('<OrderSearch orderid="%(orderid)s"/>')
    body.append(OrderSearch)    
    root.append(head)
    root.append(body)
    return et.tostring(root, xml_declaration=True, encoding='utf8')

def make_OrderFilterService():
    root =  et.XML('<Request service="OrderFilterService" lang="zh-CN"></Request>')
    head = et.XML('<Head>%(CHECKHEADER)s</Head>')
    body = et.XML('<Body></Body>') 
    OrderFilter = et.XML('<OrderFilter orderid="%(orderid)s" filter_type="1" d_address="%(d_address)s"></OrderFilter>') 
    OrderFilterOption = et.XML('<OrderFilterOption j_tel="%(j_tel)s" j_address="%(j_address)s" d_tel="%(d_tel)s" j_custid="%(j_custid)s"/>')
    OrderFilter.append(OrderFilterOption)
    body.append(OrderFilter)
    root.append(head)
    root.append(body)
    return et.tostring(root, xml_declaration=True, encoding='utf8')

def make_xml_template():
    res = {
        'OrderFilterService': make_OrderFilterService(),
        'OrderSearchService': make_OrderSearchService(),
    }
    return res


class SF_API(object):
    xml_template = make_xml_template()
    _url = 'https://bspoisp.sit.sf-express.com:11443/bsp-oisp/sfexpressService'

    def __init__(self, CHECKHEADER='BSPdevelop', CHECKBODY='j8DzkIFgmlomPt0aLuwU' ):
        self.CHECKHEADER = CHECKHEADER
        self.CHECKBODY = CHECKBODY
        
    def _Make_Sign(self, xml_str):
        s = xml_str + self.CHECKBODY;
        return base64.b64encode(md5(s).digest())
        
    def _sf_post(self, xml_str):
        arg = {
            "xml" : xml_str,
            "verifyCode" : self._Make_Sign(xml_str),   
        }
        postdata = urllib.urlencode(arg)
        req = urllib2.Request(self._url, postdata)
        #todo  process except
        respone = urllib2.urlopen(req)
        return respone
                
    def sf_post(self, name, data):
        data.update({'CHECKHEADER': self.CHECKHEADER})
        xml_str = self.xml_template[name] % data
        response = self._sf_post(xml_str)
        return  response.read()



class SF_OPEN_API(object):

    #_url = https://open-sbox.sf-express.com/public/v1.0/security/access_token/sf_appid/99999999/sf_appkey/691EF6B3E08FB629E1BBFE1DA596986E

    _url = 'https://open-sbox.sf-express.com'
    _version = 'v1.0'


    def __init__(self, sf_appid=False, sf_appkey=False, ttype='reset'):
        '''
        :param sf_appid:
        :param type: reset or public,  public type used of tets
        :return:
        '''

        self.app_id = sf_appid
        self.appkey = sf_appkey
        self.type = ttype

        if ttype == 'public':
            self.app_id = '99999999'
            self.appkey = '691EF6B3E08FB629E1BBFE1DA596986E'


    def set_app(self, appid=False, appkey=False):
        if appid:
            self.appid = appid
        if appkey:
            self.appkey = appkey

    def get_access_token(self):

        action = 'access_token'

        url = r'/'.join([self._url, self.type, self._version, 'security', action, 'sf_appid', self.app_id, 'sf_appkey', self.appkey ])

        print url
        head = {
            "transType" : '301',
            "transMessageId" : '201408192052000001',
        }
        postdata = urllib.urlencode(head)
        req = urllib2.Request(url, postdata)

        respone = urllib2.urlopen(req)
        print   respone.read()










        
        
        

#############################################################################################
if __name__ == '__main__':

    sf = SF_OPEN_API(ttype = 'public')

    #sf.get_access_token()



    order_data = {
    'orderid' : 'TE20150104',
    'd_address' : 'hunnan changsha xingsha',
    'j_tel':'13810744',
    'j_address':'hunnan xxxxx',
    'd_tel': '123456879',
    'j_custid':'ddfdf',
    }
    res = sf.sf_post('OrderFilterService', order_data)
    print  res
    
    print sf.sf_post('OrderSearchService', {'orderid': 'TE20150104'} )
        
  
        

