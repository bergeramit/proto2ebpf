import re

class ProtobufBasicRule:
    '''
    Example rules:
            "person.email == joe@gmail.com"
            "search.query ~ dog"
    '''
    def __init__(self, proto_class, str_rule) -> None:
        self.proto_class = proto_class
        match_rule_pattern = re.search('(?P<class>\w+).(?P<field>\w+) (?P<operator>.*) (?P<value>.*)', str_rule)
        
        # Maybe uneeded
        self.class_name = match_rule_pattern.group('class')

        self.field_name = match_rule_pattern.group('field')
        self.field_number = self.proto_class.DESCRIPTOR.fields_by_name[self.field_name].number

        self.operator = match_rule_pattern.group('operator')
        self.value = match_rule_pattern.group('value')

    def generate_c_code_rule(self, pointer):
        print(f"Pointer: {pointer}")
        if self.operator == '~':
            # Search for specific string
            _dict = {
                "array_value": ", ".join([str(ord(c)) for c in self.value]),
                "pointer": pointer,
                "array_size": len(self.value)
            }
            return '''
                unsigned long target_value = {{ {array_value} }};
                bool found = false;
                for (i = 2; i < payload_length; i++) {{
                    if (memcmp(&({pointer}[i]), target_value, {array_size}) == 0){{
                        found = true;
                    }}
                }}
                if (found) {{
                    goto DROP;
                }}'''.format(**_dict)
        raise Exception("CANNOT PARSE OPERATOR")
