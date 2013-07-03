# -*- coding: utf-8 -*-

from xml.etree import ElementTree

class MetaParser(object):
    def GetResources(self):
        pass
    
    def GetRetsClass(self, resource):
        pass
    
    def GetTables(self, resource, rets_class):
        pass
    
    def GetLookUp(self, resource, rets_class):
        pass
    

class StandardXmlMetaParser(MetaParser):
    def __init__(self, filepath):
        with open(filepath,'r') as f:
            xml_str = f.read()
        
        self.meta_xml = ElementTree.fromstring(xml_str)
        
    def GetResources(self):
        resource_list = []
        resource_xml_list = self.meta_xml.find('METADATA').find('METADATA-SYSTEM').find('SYSTEM').find('METADATA-RESOURCE').findall('Resource')
        for resource_xml in resource_xml_list:
            resource = RetsResource()
            resource.resource_id = resource_xml.find('ResourceID').text
            resource_list.append(resource)
        return resource_list
    
    def GetRetsClass(self, resource):
        class_list = []
        resource_xml_list = self.meta_xml.find('METADATA').find('METADATA-SYSTEM').find('SYSTEM').find('METADATA-RESOURCE').findall('Resource')
        for resource_xml in resource_xml_list:
            if resource_xml.find('ResourceID')==resource:
                class_xml_list = resource_xml.findall('Class')
                for class_xml in class_xml_list:
                    
    
    def GetTables(self, resource, rets_class):
        pass
    
    def GetLookUp(self, resource, rets_class):
        pass

class RetsResource(object):
    def __init__(self):
        self.resource_id = None
        
class RetsClass(object):
    def __init__(self):
        self.rets_classname = None
        
class RetsTable(object):
    def __init__(self):
        self.system_name = None
        
    
