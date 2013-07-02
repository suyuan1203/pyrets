import requests
from xml.etree import ElementTree
from urllib.parse import urlparse, urljoin
import socket
import hashlib
import time


class RetsSession(object):
    def __init__(self, user, passwd, user_agent, rets_version, login_url, user_agent_passwd=None):
        self.rets_ua_authorization = None
        self.user = user
        self.passwd = passwd
        self.user_agent = user_agent
        self.user_agent_passwd = user_agent_passwd
        self.rets_version = rets_version
        self.base_url = self._get_base_url(login_url)
        self.login_url = login_url
        self._session = None

    def login(self):
        self._session = requests.session()
        
        headers = {'User-Agent':self.user_agent,
               'RETS-Version':self.rets_version,
               'Accept':"*/*"}
        
        if self.user_agent_passwd:
            headers['RETS-UA-Authorization'] = self._calculate_rets_ua_authorization(''
                                                                            , self.user_agent
                                                                            , self.user_agent_passwd
                                                                            , self.rets_version)
            
        auth = requests.auth.HTTPDigestAuth(self.user, self.passwd)
        
        self._session.headers = headers
        self._session.auth = auth

        login_result = self._session.get(self.login_url)
        
        self.rets_server_info = self._parse_login_response(login_result.text)
        
        if self.user_agent_passwd:
            self.rets_ua_authorization = self._calculate_rets_ua_authorization(login_result.cookies['RETS-Session-ID']
                                                                            , self.user_agent
                                                                            , self.user_agent_passwd
                                                                            , self.rets_version)
        return login_result.text

    def logout(self):
        logout_url = urljoin(self.base_url, self.rets_server_info['Logout'])
        self._set_rets_ua_authorization()
        logout_response = self._session.get(logout_url)
        return logout_response.text

    def getobject(self):
        for i in range(3):
            try:
                return self._getobject()
            except socket.timeout:
                if i < 3:
                    print('timeout, try again')
                    time.sleep(5)
                else:
                    raise
                
    def getmetadata(self):
        get_meta_url = urljoin(self.base_url, self.rets_server_info['GetMetadata'])
        self._set_rets_ua_authorization()
        metadata_text = self._session.get(get_meta_url + '?Type=METADATA-SYSTEM&ID=*&Format=STANDARD-XML')
        return metadata_text.text
                
    def _get_base_url(self, url_str):
        url_parts = urlparse(url_str)
        resURL = url_parts.scheme + "://" + url_parts.netloc
        return resURL

    def _getobject(self, obj_type, resource , obj_id):
        getobject_url = urljoin(self.base_url, self.rets_server_info['GetObject'])
        self._set_rets_ua_authorization()
        getobject_response = self._session.get(getobject_url+"?Type=%s&Resource=%s&ID=%s" % (obj_type, resource, ))
        return getobject_response.content

    def _parse_login_response(self, login_resp):
        login_xml = ElementTree.fromstring(login_resp)
        reply_code = login_xml.attrib['ReplyCode']
        reply_text = login_xml.attrib['ReplyText']
        if reply_code != '0':
            raise LoginException(reply_code + "," + reply_text)
        if len(login_xml) > 0:
            rets_info = login_xml[0].text.split('\n')
        else:
            #for servers which don't have RETS-RESPONSE node
            rets_info = login_xml.text.split('\n')
        rets_info_dict = {}
        for info_item in rets_info:
            if info_item.strip():
                key_value_pair = info_item.split('=')
                rets_info_dict[key_value_pair[0].strip()] = key_value_pair[1].strip()
        return rets_info_dict
    
    def _set_rets_ua_authorization(self):
        self._session.headers['RETS-UA-Authorization'] = self.rets_ua_authorization;

    def _calculate_rets_ua_authorization(self, sid, user_agent, user_agent_passwd, rets_version):
        product = user_agent
        a1hashed = hashlib.md5(bytes(product + ':' + user_agent_passwd, 'utf-8')).hexdigest()
        retsrequestid = ''
        retssessionid = sid
        digestHash = hashlib.md5(bytes(a1hashed + ':' + retsrequestid + ':' + retssessionid + ':' + rets_version, 'utf-8')).hexdigest()
        return 'Digest ' + digestHash
    
class LoginException(Exception):
    pass   


    
