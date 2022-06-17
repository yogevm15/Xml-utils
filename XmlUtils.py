# imports
import re

import FileHandler
from XmlSyntaxException import *
import collections.abc

def parse_from_file(path):
    """Read xml file and parse it into list of elements

        :param path: The path to the xml file.
        :type path: str
        :return: A list of element, each element is dict with the keys: "name" for the name, "attributes" for the attributes dict and "inner" for all inner elements and raw content.
        :rtype: list
    """
    parser = XmlParser()
    return parser.parse(FileHandler.get_file_content(path), path)


def parse_from_str(content):
    """Parse xml str into list of elements

        :param content: The xml content.
        :type content: str
        :return: A list of element, each element is dict with the keys: "name" for the name, "attributes" for the attributes dict and "inner" for all inner elements and raw content.
        :rtype: list
    """
    parser = XmlParser()
    return parser.parse(content, "Xml file")


def serialize_to_file(elements, path):
    """Serialize list of element into xml file

        :param path: The path to the new xml file.
        :type path: str
        :param elements: The list of elements.
        :type elements: list
        :rtype: None
    """
    FileHandler.write_to_file(serialize(elements, 0), path)


def serialize_to_str(elements):
    """Serialize list of element into xml str

        :param elements: The list of elements.
        :type elements: list
        :return: A xml str
        :rtype: str
    """
    return serialize(elements, 0)


def serialize(elements, level):
    to_return = ""
    for element in elements:
        if 'type' in element and element['type'] == 'comment':
            to_return += "\t" * level + "<!--" + element["inner"]+'-->\n'
        else:
            to_return += "\t" * level + "<" + element["name"]
            if "attributes" not in element:
                element["attributes"] = {}
            if "inner" not in element:
                element["inner"] = []
            for key, value in element["attributes"].items():
                to_return += "\n" + "\t" * (level + 1) + key + "=\"" + value + "\""
            if isinstance(element["inner"], collections.abc.Sequence) and not isinstance(element["inner"], str):
                if len(element["inner"]) > 0:
                    to_return += ">\n" + serialize(element["inner"], level + 1) + "\t" * level +"</" + element["name"] + ">\n"
                else:
                    to_return += "/>\n"
            elif type(element["inner"]) is not None:
                to_return += ">" + str(element["inner"]) + "</" + element["name"] + ">\n"
            else:
                to_return += "/>\n"
    return to_return


class XmlParser:
    # data
    all_lines = []  # List of all lines in xml_content.
    parsed_data = []  # List of elements to return.
    xml_content = ""  # Whole xml content

    # indexes
    curr_char_index_in_line = 0  # Current index in the line.
    curr_line_index = 0  # Current line index in all_lines.
    curr_value = ""  # Current temporary value is variable used to store element name, attribute name, attribute value etc.
    curr_level = [0]  # Current index for place in the nested xml Ex. [0,1] in the second element inner first.
    curr_attribute = ""  # Current temporary attribute name used by create_attribute function.
    curr_char_index_in_all_content = -1  # Current index in all xml_content.
    curr_attribute_name_line_index = 0  # Line index in all_lines for the last attribute name.
    curr_attribute_name_char_index_in_line = 0  # Index in the line for the last attribute name.

    # Flags for current parsing situation.
    is_reading_attribute_name = False  # True when reading attribute name.
    is_reading_attribute_value = False  # True when reading attribute value.
    is_reading_element_name = False  # True when reading element name.
    is_reading_close_element_name = False  # True when reading name after "</" Ex. </Example.
    is_start = False  # Temporary flag for reading names and values True when start reading.
    is_closing = False  # Temporary flag, True when "/" after reading element name or attribute name or attribute value.
    file_path = ""

    def __init__(self):
        self.all_lines = []
        self.parsed_data = []
        self.xml_content = ""
        self.curr_char_index_in_line = 0
        self.curr_line_index = 0
        self.curr_value = ""
        self.curr_level = [0]
        self.curr_attribute = ""
        self.curr_char_index_in_all_content = -1
        self.curr_attribute_name_line_index = 0
        self.curr_attribute_name_char_index_in_line = 0
        self.is_reading_attribute_name = False
        self.is_reading_attribute_value = False
        self.is_reading_element_name = False
        self.is_reading_close_element_name = False
        self.is_start = False
        self.is_closing = False
        self.file_path = ""

    # Main parse function
    def parse(self, xml_content, file_path):
        self.file_path = file_path

        # Remove the comments.
        self.xml_content = self.remove_comments(xml_content)

        # Split the lines.
        self.all_lines = xml_content.split("\n")

        # Iterate all chars in xml_content
        for curr_char in self.xml_content:
            # Handle indexes.
            self.handle_indexes(curr_char)
            # Handle syntax exceptions.
            self.handle_exceptions(curr_char)
            # Handle current state.
            self.handle_parse_situation(curr_char)
        return self.parsed_data

    # Handle curr line and curr place in line for syntax errors debug
    def handle_indexes(self, curr_char):
        self.curr_char_index_in_all_content += 1
        if curr_char == '\n':
            self.curr_line_index += 1
            self.curr_char_index_in_line = 0
        elif curr_char == '\t':
            self.curr_char_index_in_line += 4
        else:
            self.curr_char_index_in_line += 1

    # Handle the parsing situation.
    def handle_parse_situation(self, curr_char):
        if self.is_reading_element_name:
            self.read_element_name(curr_char)
        elif self.is_reading_attribute_name:
            self.read_attribute_name(curr_char)
        elif self.is_reading_attribute_value:
            self.read_attribute_value(curr_char)
        elif self.is_reading_close_element_name:
            self.read_close_element_name(curr_char)
        else:
            self.read_raw(curr_char)

    # Read raw content.
    def read_raw(self, curr_char):
        if curr_char == "<" and len(self.xml_content) > self.curr_char_index_in_all_content + 1 and \
                self.xml_content[self.curr_char_index_in_all_content + 1] == "/":
            self.is_start = True
            self.is_reading_close_element_name = True
        elif curr_char == "<":
            self.is_start = True
            self.is_reading_element_name = True
        elif self.is_closing and curr_char == ">":
            self.is_closing = False
        elif curr_char != "\t" and curr_char != "\n" and curr_char != " ":
            self.insert_text_content(curr_char)

    # Read element name.
    def read_element_name(self, curr_char):
        if curr_char == "/":
            self.is_closing = True
            self.create_element({"name": self.curr_value, "attributes": {}, "inner": []})
            self.is_reading_element_name = False
            self.curr_level[-1] += 1
            self.curr_value = ""
            self.is_start = False
        elif curr_char == ">":
            self.create_element({"name": self.curr_value, "attributes": {}, "inner": []})
            self.curr_level.append(0)
            self.curr_value = ""
            self.is_start = False
            self.is_reading_element_name = False
        elif self.is_start:
            if curr_char == "\t" or curr_char == "\n" or curr_char == " ":
                self.create_element({"name": self.curr_value, "attributes": {}, "inner": []})
                self.curr_value = ""
                self.is_start = False
                self.is_reading_attribute_name = True
                self.is_reading_element_name = False
            else:
                self.curr_value += curr_char

    # Read closing element name.
    def read_close_element_name(self, curr_char):
        if curr_char == ">":
            self.check_element_closed(self.curr_value)
            self.curr_value = ""
            self.is_start = False
            self.is_reading_close_element_name = False
        elif self.is_start:
            if curr_char == "\t" or curr_char == "\n" or curr_char == " ":
                self.create_element({"name": self.curr_value, "attributes": {}, "inner": []})
                self.curr_value = ""
                self.is_start = False
                self.is_reading_attribute_name = True
                self.is_reading_element_name = False
            else:
                self.curr_value += curr_char

    # Read attribute name.
    def read_attribute_name(self, curr_char):
        if self.is_start:
            if curr_char == "\t" or curr_char == "\n" or curr_char == " ":
                self.curr_attribute = self.curr_value
                self.curr_value = ""
                self.is_start = False
                self.is_reading_attribute_name = False
                self.is_reading_attribute_value = True
                if self.curr_char_index_in_line == 0:
                    self.curr_attribute_name_char_index_in_line = -1
                    self.curr_attribute_name_line_index = self.curr_line_index - 1
                else:
                    self.curr_attribute_name_char_index_in_line = self.curr_char_index_in_line - 1
                    self.curr_attribute_name_line_index = self.curr_line_index
            elif curr_char == "=":
                self.curr_attribute = self.curr_value
                self.curr_value = "="
                self.is_start = False
                self.is_reading_attribute_name = False
                self.is_reading_attribute_value = True
                if self.curr_char_index_in_line == 0:
                    self.curr_attribute_name_char_index_in_line = -1
                    self.curr_attribute_name_line_index = self.curr_line_index - 1
                else:
                    self.curr_attribute_name_char_index_in_line = self.curr_char_index_in_line - 1
                    self.curr_attribute_name_line_index = self.curr_line_index
            else:
                self.curr_value += curr_char
        elif not (curr_char == "\t" or curr_char == "\n" or curr_char == " "):
            if curr_char == "/":
                self.is_closing = True
                self.is_reading_attribute_name = False
                self.curr_level[-1] += 1
                self.curr_value = ""
                self.is_start = False
            elif curr_char == ">":
                self.is_reading_attribute_name = False
                self.curr_level.append(0)
                self.curr_value = ""
                self.is_start = False
            else:
                self.is_start = True
                self.curr_value += curr_char

    # Read attribute value.
    def read_attribute_value(self, curr_char):
        if self.is_start:
            if curr_char == self.curr_value[0]:
                self.curr_value = self.curr_value[1:]
                self.create_attribute(self.curr_value)
                self.curr_value = ""
                self.is_start = False
                self.is_reading_attribute_name = True
                self.is_reading_attribute_value = False
            else:
                self.curr_value += curr_char
        else:
            if not (curr_char == "\t" or curr_char == "\n" or curr_char == " "):
                self.curr_value += curr_char
                if self.curr_value == "=\"" or self.curr_value == "=\'":
                    self.is_start = True
                    self.curr_value = curr_char

    # Create element in list or in inner elements.
    def create_element(self, dict_data):
        pattern = "^(?!XML)[_a-zA-Z][\w0-9-]*"  # regex for element and attribute name
        if not re.match(pattern, dict_data["name"]):
            raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                     self.curr_line_index, "bad_element_name", self.file_path)
        inner_list = self.parsed_data
        for i in range(len(self.curr_level) - 1):
            inner_list = inner_list[self.curr_level[i]]["inner"]
        inner_list.append(dict_data)
        self.curr_level[-1] = len(inner_list) - 1

    # check if the close name match the element name.
    def check_element_closed(self, element_name):
        element_name = element_name[1:]
        inner_dict = {"inner": self.parsed_data}
        self.curr_level.pop()
        for i in self.curr_level:
            inner_dict = inner_dict["inner"][i]
        if element_name != inner_dict["name"]:
            raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                     self.curr_line_index, "bad_end_tag", self.file_path)

    # Create attribute in the matching element.
    def create_attribute(self, attribute_value):
        inner_dict = {"inner": self.parsed_data}
        for i in self.curr_level:
            inner_dict = inner_dict["inner"][i]
        inner_dict["attributes"][self.curr_attribute] = attribute_value

    # Insert Raw content in matching element.
    def insert_text_content(self, content):
        inner_list = self.parsed_data
        for i in range(len(self.curr_level) - 1):
            inner_list = inner_list[self.curr_level[i]]["inner"]
        if len(inner_list) <= self.curr_level[-1]:
            inner_list.append(content)
        else:
            inner_list[self.curr_level[-1]] += content

    # Simple function to remove all xml comments.
    @staticmethod
    def remove_comments(xml_content):
        return re.sub("(?s)<!--.*?-->", "", xml_content)

    # Handle most of the exceptions.
    def handle_exceptions(self, curr_char):
        pattern = "^(?!XML)[_a-zA-Z][\w0-9-]*"  # regex for element and attribute name
        if not self.is_reading_attribute_value:
            if self.is_closing and curr_char != ">":
                self.change_to_last_char()
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "bad_close", self.file_path)
            elif self.is_reading_element_name and not re.match(pattern, self.curr_value) and self.curr_value != "":
                self.change_to_last_char()
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "bad_element_name", self.file_path)
            elif self.is_reading_element_name and self.curr_value == "" and (curr_char == " " or
                                                                             curr_char == "\t" or
                                                                             curr_char == "\n"):
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "bad_element_name", self.file_path)
            elif self.is_reading_attribute_name and not re.match(pattern, self.curr_value) and self.curr_value != "":
                self.change_to_last_char()
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "bad_attribute_name", self.file_path)
            elif self.is_reading_attribute_name and (curr_char == ">" or curr_char == "<" and self.curr_value != ""):
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "no_value", self.file_path)
            elif curr_char == "<" and (
                    self.is_reading_element_name or
                    self.is_reading_attribute_value or
                    self.is_reading_attribute_name):
                raise XmlSyntaxException(self.curr_char_index_in_line, self.all_lines[self.curr_line_index],
                                         self.curr_line_index, "not_closed", self.file_path)
        elif not self.is_start and \
                curr_char != "=" and \
                curr_char != "\'" and \
                curr_char != "\"" and \
                curr_char != " " and \
                curr_char != "\t" and \
                curr_char != "\n":
            raise XmlSyntaxException(self.curr_attribute_name_char_index_in_line,
                                     self.all_lines[self.curr_attribute_name_line_index],
                                     self.curr_attribute_name_line_index, "no_value", self.file_path)

    # Go back to last index used for debug.
    def change_to_last_char(self):
        if self.curr_char_index_in_line == 0:
            self.curr_char_index_in_line = -1
            self.curr_line_index -= 1
        else:
            self.curr_char_index_in_line -= 1
