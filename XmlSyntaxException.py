class XmlSyntaxException(Exception):
    def __init__(self, char_num, line_content, line_num, error_type, file_path):
        line_content = line_content.replace("\t", "    ")
        self.errors = "In " + file_path + ":\n"
        if error_type == 'not_closed':
            self.errors += "Cannot open tag before closing tag.\n"
        elif error_type == 'bad_end_tag':
            self.errors += "Element must be terminated by the matching end-tag.\n"
        elif error_type == 'bad_element_name':
            self.errors += "Element name error.\n"
        elif error_type == 'bad_close':
            self.errors += "Element must be closed by > or />.\n"
        elif error_type == 'bad_attribute_name':
            self.errors += "Attribute name error.\n"
        elif error_type == 'no_value':
            self.errors += "Attribute name must be followed by the =\" or =\' characters.\n"

        self.errors += "In line " + str(line_num + 1) + ":\n"
        self.errors += "\t" + line_content + "\n"
        if char_num == -1:
            self.errors += "\t" + " " * (len(line_content) - 1) + "^"
        else:
            self.errors += "\t" + " " * (char_num - 1) + "^"

    def __str__(self):
        return str(self.errors)
