# -*- coding: utf-8 -*-

from xml.etree import ElementTree

class MetaParser(object):
    def get_all_resource(self):
        pass
    
    def get_resource(self, resource_id):
        pass
    
    def get_all_retsclass(self, resource_id):
        pass
    
    def get_retsclass(self, resource_id, retsclass_name):
        pass
    
    def get_all_field(self, resource_id, retsclass_name):
        pass
    
    def get_field(self, resource_id, retsclass_name, field_system_name):
        pass
    
    def get_all_lookup(self, resource_id, retsclass_name, field_system_name):
        pass
    
    def get_lookup(self, resource_id, retsclass_name, field_system_name, lookup_name):
        pass
    
    def get_all_lookup_type(self, resource_id, lookup_name):
        pass
    

class StandardXmlMetaParser(MetaParser):
    def __init__(self, filepath):
        with open(filepath,'r') as f:
            xml_str = f.read()
        
        self.meta_xml = ElementTree.fromstring(xml_str)
        
    def get_all_resource(self):
        resource_list = []
        resource_xml_list = self._get_all_resource_xml()
        for resource_xml in resource_xml_list:
            resource = RetsResource()
            resource.resource_id = resource_xml.find('ResourceID').text
            resource_list.append(resource)
        return resource_list
    
    def get_resource(self, resource_id):
        resource_list = self.get_all_resource()
        for resource in resource_list:
            if resource.resource_id == resource_id:
                return resource
    
    def get_all_retsclass(self, resource_id):
        class_list = []
        class_xml_list = self._get_all_retsclass_xml(resource_id)
        for class_xml in class_xml_list:
            rets_class = RetsClass()
            rets_class.retsclass_name = class_xml.find('ClassName').text
            class_list.append(rets_class)
        return class_list
    
    def get_retsclass(self, resource_id, retsclass_name):
        rets_class_list = self.get_all_retsclass(resource_id)
        for rets_class in rets_class_list:
            if rets_class.retsclass_name == retsclass_name:
                return rets_class
    
    def get_all_field(self, resource_id, retsclass_name):
        field_list = []
        field_xml_list = self._get_all_field_xml(resource_id, retsclass_name)
        for field_xml in field_xml_list:
            rets_field = RetsField()
            rets_field.system_name = field_xml.find('SystemName').text
            field_list.append(rets_field)
        return field_list
    
    def get_field(self, resource_id, retsclass_name, field_system_name):
        field_list = self.get_all_field(resource_id, retsclass_name)
        for field in field_list:
            if field.system_name == field_system_name:
                return field
            
    def get_all_lookup(self, resource_id):
        lookup_list = []
        lookup_xml_list = self._get_all_lookup_xml(resource_id)
        for lookup_xml in lookup_xml_list:
            lookup = RetsLookup()
            lookup.lookup_name = lookup_xml.find('LookupName').text
            lookup_list.append(lookup)
        return lookup_list
    
    def get_lookup(self, resource_id, lookup_name):
        lookup_list = self.get_all_lookup(resource_id)
        for lookup in lookup_list:
            if lookup.lookup_name == lookup_name:
                return lookup
            
    def get_all_lookup_type(self, resource_id, lookup_name):
        lookup_list = []
        lookup_type_xml_list = self._get_all_lookup_type_xml(resource_id, lookup_name)
        for lookup_type_xml in lookup_type_xml_list:
            lookup_type = RetsLookupType()
            lookup_type.value = lookup_type_xml.find('Value').text
            lookup_type.longvalue = lookup_type_xml.find('LongValue').text
            lookup_type.shortvalue = lookup_type_xml.find('ShortValue').text
            lookup_list.append(lookup_type)
        return lookup_list
        
    def _get_resource_xml(self, resource_id):
        resource_xml_list = self._get_all_resource_xml()
        for resource_xml in resource_xml_list:
            if resource_id == resource_xml.find('ResourceID').text:
                return resource_xml 
    
    def _get_all_resource_xml(self):
        resource_xml_list = self.meta_xml.find('METADATA').find('METADATA-SYSTEM').find('SYSTEM').find('METADATA-RESOURCE').findall('Resource')
        return resource_xml_list
    
    def _get_all_retsclass_xml(self, resource_id):
        resource_xml = self._get_resource_xml(resource_id)
        return resource_xml.find('METADATA-CLASS').findall('Class')
    
    def _get_retsclass_xml(self, resource_id, retsclass_name):
        class_xml_list = self._get_all_retsclass_xml(resource_id)
        for class_xml in class_xml_list:
            if retsclass_name == class_xml.find('ClassName').text:
                return class_xml
            
    def _get_all_field_xml(self, resource_id, retsclass_name):
        class_xml = self._get_retsclass_xml(resource_id, retsclass_name)
        return class_xml.find('METADATA-TABLE').findall('Field')
    
    def _get_field_xml(self, resource_id, retsclass_name, field_system_name):
        field_xml_list = self._get_all_field_xml(resource_id, retsclass_name)
        for field_xml in field_xml_list:
            if field_system_name == field_xml.find('SystemName').text:
                return field_xml
            
    def _get_all_lookup_xml(self, resource_id):
        resource_xml = self._get_resource_xml(resource_id)
        return resource_xml.find('METADATA-LOOKUP').findall('Lookup')
    
    def _get_lookup_xml(self, resource_id, lookup_name):
        lookup_xml_list = self._get_all_lookup_xml(resource_id)
        for lookup_xml in lookup_xml_list:
            if lookup_xml.find('LookupName').text == lookup_name:
                return lookup_xml
            
    def _get_all_lookup_type_xml(self, resource_id, lookup_name):
        lookup_xml = self._get_lookup_xml(resource_id, lookup_name)
        return lookup_xml.find('METADATA-LOOKUP_TYPE').findall('LookupType')
    
class RetsResource(object):
    def __init__(self):
        self.resource_id = None
        
class RetsClass(object):
    def __init__(self):
        self.retsclass_name = None
        
class RetsField(object):
    def __init__(self):
        self.system_name = None
        
class RetsLookup(object):
    def __init__(self):
        self.lookup_name = None
        
class RetsLookupType(object):
    def __init__(self):
        self.value = None
        self.longvalue = None
        self.shortvalue = None


if __name__ == '__main__':
    meta_parser = StandardXmlMetaParser('/home/rsu/110 Metadata.xml')
    resource_list = meta_parser.get_all_resource()
    print([x.resource_id for x in resource_list])
    
    retsclass_list = meta_parser.get_all_retsclass('Property')
    print([x.retsclass_name for x in retsclass_list])
    
    field_list = meta_parser.get_all_field('Property', 'BUSO')
    print([x.system_name for x in field_list])
    
    lookup_list = meta_parser.get_all_lookup('Property')
    print([x.lookup_name for x in lookup_list])
    
    lookup_type_list = meta_parser.get_all_lookup_type('Property', 'AgreementType')
    print([x.value for x in lookup_type_list])
    
