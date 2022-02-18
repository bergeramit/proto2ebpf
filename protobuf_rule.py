import re

class ProtobufBasicRule:
    '''
    Example rules:
            "person.email == 'joe@gmail.com'"
            "search.query ~ '*dog'"
    '''
    def __init__(self, proto_class, str_rule) -> None:
        self.proto_class = proto_class
        match_rule_pattern = re.search('(?P<class>\w+).(?P<field>\w+) (?P<operator>.*) (?P<value>.*)', str_rule)
        
        # Maybe uneeded
        self.class_name_ = match_rule_pattern.group('class')

        self.field_name_ = match_rule_pattern.group('field')
        self.field_descriptor_ = self.proto_class.DESCRIPTOR.fields_by_name[self.field_name_]

        self.operator = match_rule_pattern.group('operator')
        self.value = match_rule_pattern.group('value')
