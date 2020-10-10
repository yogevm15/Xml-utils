# Xml-utils
Basic python xml utils such as parser and serializer
# Usage
### Import:
from XmlUtils import parse_from_file, parse_from_str, serialize_to_file, serialize_to_str

### Functions:
#### parse_from_file(path):
Read xml file and parse it into list of elements

param path: str - The path to the xml file.
return: list - A list of element, each element is dict with the keys: "name" for the name, "attributes" for the attributes dict and "inner" for all inner elements and raw content.

#### parse_from_str(content):
Read xml file and parse it into list of elements

param content: str - The xml content.
return: list - A list of element, each element is dict with the keys: "name" for the name, "attributes" for the attributes dict and "inner" for all inner elements and raw content.

#### serialize_to_file(elements):
Serialize list of element into xml file

param elements: list - The list of elements.
param path: str - The path to the new xml file.
return: None.

#### serialize_to_str(elements):
Serialize list of element into xml str

param elements: list - The list of elements.
return: str -  A xml str.


