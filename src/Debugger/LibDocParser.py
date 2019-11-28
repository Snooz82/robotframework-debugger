from xml.dom import minidom


class LibDocParser:

    def __init__(self):

        self.input_xml_file_path = None

        self.libdoc_xml = None

        self.library_name = ''
        self.library_version = ''
        self.library_keywords = []

        self.library_as_dictionary = {}

    def parse_libdoc_xml(self, input_xml_file_path):
        self.input_xml_file_path = input_xml_file_path
        self._parse_xml_from_file()
        self._get_library_name()
        self._get_library_version()
        self._get_library_keywords()
        self._create_lib_dict_from_data()
        if len(self.library_keywords) > 0:
            return self.library_as_dictionary

    def _parse_xml_from_file(self):
        self.libdoc_xml = minidom.parse(self.input_xml_file_path)

    def _get_library_name(self):
        keywordspec = self.libdoc_xml.getElementsByTagName('keywordspec')
        self.library_name = keywordspec[0].attributes['name'].value

    def _get_library_version(self):
        version = self.libdoc_xml.getElementsByTagName('version')
        if version[0].firstChild:
            self.library_version = version[0].firstChild.data

    def _get_library_keywords(self):
        array_of_kw = self.libdoc_xml.getElementsByTagName('kw')
        for i, kw in enumerate(array_of_kw):
            if i == (len(self.library_keywords)):
                self.library_keywords.append(dict())
            self.library_keywords[i]['name'] = kw.attributes['name'].value
            arguments = kw.getElementsByTagName('arg')
            self.library_keywords[i]['args'] = []
            if arguments:
                for arg in arguments:
                    self.library_keywords[i]['args']. \
                        append(arg.firstChild.data)
            doc = kw.getElementsByTagName('doc')[0].firstChild
            if doc:
                doc_text = doc.data
                self.library_keywords[i]['doc'] = doc_text
            else:
                self.library_keywords[i]['doc'] = ''

    def _create_lib_dict_from_data(self):
        self.library_as_dictionary['name'] = self.library_name
        self.library_as_dictionary['version'] = self.library_version
        self.library_as_dictionary['keywords'] = self.library_keywords