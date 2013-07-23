# -*- coding: utf-8 -*-

import requests
from xml.etree import ElementTree
from urllib.parse import urlparse, urljoin
import socket
import hashlib
import time
import urllib.parse


class RetsSession(object):
    def __init__(self, user, passwd, user_agent, user_agent_passwd, rets_version, login_url):
        self.rets_ua_authorization = None
        self.user = user
        self.passwd = passwd
        self.user_agent = user_agent
        self.user_agent_passwd = user_agent_passwd
        self.rets_version = rets_version
        self.base_url = self._get_base_url(login_url)
        self.login_url = login_url
        self._session = None
        self.login_called = False

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
        login_result.raise_for_status()
        
        self.server_info = self._parse_login_response(login_result.text)
        
        if self.user_agent_passwd:
            self.rets_ua_authorization = self._calculate_rets_ua_authorization(login_result.cookies['RETS-Session-ID']
                                                                            , self.user_agent
                                                                            , self.user_agent_passwd
                                                                           , self.rets_version)
        self.login_called = True
        return login_result.text

    def logout(self):
        if not self.login_called:
            raise NoLoginException("You need to call login before logout")
        
        logout_url = urljoin(self.base_url, self.server_info['Logout'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        logout_response = self._session.get(logout_url)
        logout_response.raise_for_status()
        return logout_response.text

    def getobject(self, obj_type, resource , obj_id):
        if not self.login_called:
            raise NoLoginException("You need to call login before getobject")
        
        for i in range(3):
            try:
                return self._getobject(obj_type, resource , obj_id)
            except socket.timeout:
                if i < 3:
                    print('timeout, try again')
                    time.sleep(5)
                else:
                    raise
                
    def getmetadata(self):
        if not self.login_called:
            raise NoLoginException("You need to call login before getmetadata")
        
        get_meta_url = urljoin(self.base_url, self.server_info['GetMetadata'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        response = self._session.get(get_meta_url + '?Type=METADATA-SYSTEM&ID=*&Format=STANDARD-XML')
        response.raise_for_status()
        self._parse_getmetadata_response(response.text)
        return response.text
    
    def search(self, resource, search_class, query, limit, select):
        if not self.login_called:
            raise NoLoginException("You need to call login before search")
        
        if limit:
            limit = 'NONE'
        params = {'SearchType': resource,
                  'Class': search_class,
                  'Query': query,
                  'QueryType': 'DMQL2',
                  'Count': '0',
                  'Format': 'COMPACT-DECODED',
                  'Limit': limit,
                  'Select': select,
                  'StandardNames': '0'}
        search_url = urljoin(self.base_url, self.server_info['Search'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        search_response = self._session.post(search_url, params)
        search_response.raise_for_status()
        self._parse_search_response(search_response.text)
        return search_response.text
         
    def _get_base_url(self, url_str):
        url_parts = urlparse(url_str)
        resURL = url_parts.scheme + "://" + url_parts.netloc
        return resURL

    def _getobject(self, obj_type, resource , obj_id):
        getobject_url = urljoin(self.base_url, self.server_info['GetObject'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        getobject_response = self._session.get(getobject_url + "?Type=%s&Resource=%s&ID=%s" % (obj_type, resource, obj_id))
        getobject_response.raise_for_status()
        if getobject_response.headers['content-type'] == 'text/plain':
            self._parse_getobject_response(getobject_response.text)
        return getobject_response.content

    def _parse_login_response(self, login_resp):
        reply_code, reply_text = self._get_code_text(login_resp)
        if reply_code != '0':
            raise LoginException(reply_code + "," + reply_text)
        
        login_xml = ElementTree.fromstring(login_resp)
        if len(login_xml) > 0:
            rets_info = login_xml[0].text.split('\n')
        else:
            # for servers which don't have RETS-RESPONSE node
            rets_info = login_xml.text.split('\n')
        rets_info_dict = {}
        for info_item in rets_info:
            if info_item.strip():
                key_value_pair = info_item.split('=')
                rets_info_dict[key_value_pair[0].strip()] = key_value_pair[1].strip()
        return rets_info_dict
    
    def _parse_getobject_response(self, response):
        reply_code, reply_text = self._get_code_text(response)
        if reply_code != '0':
            raise GetObjectException(reply_code + "," + reply_text)
    
    def _parse_search_response(self, response):
        if not response:
            raise SearchException('Empty response')
        reply_code, reply_text = self._get_code_text(response)
        if reply_code not in ['0']:
            raise SearchException(reply_code + "," + reply_text) 
        
    def _parse_getmetadata_response(self, response):
        reply_code, reply_text = self._get_code_text(response)
        if reply_code != '0':
            raise GetMetadataException(reply_code + "," + reply_text) 
        
    def _get_code_text(self, response_xml): 
        xml_obj = ElementTree.fromstring(response_xml)
        reply_code = xml_obj.attrib['ReplyCode']
        reply_text = xml_obj.attrib['ReplyText']
        return reply_code, reply_text
        
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

class GetObjectException(Exception):
    pass

class SearchException(Exception):
    pass

class GetMetadataException(Exception):
    pass

class NoLoginException(Exception):
    pass


    

