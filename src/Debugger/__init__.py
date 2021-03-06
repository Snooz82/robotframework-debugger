# Copyright 2019-  René Rohner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import robot

from tkinter import *

from distutils.version import StrictVersion
from Debugger.DebuggerGui import DebuggerGui
from robot.libdocpkg import LibraryDocumentation

__version__ = '0.2.1'

_SUITE_SETUP = 1
_TEST_CASE = 3
_SUITE_TEARDOWN = 5
is_RF_4 = StrictVersion(robot.__version__) >= StrictVersion('4.0.0')

muting_keywords = [
    "Run Keyword And Ignore Error",
    "Run Keyword And Expect Error",
    "Run Keyword And Return Status",
    "Run Keyword And Warn On Failure",
    "Wait Until Keyword Succeeds",
]


class Debugger:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, break_on_fail=True):

        self.ROBOT_LIBRARY_LISTENER = self

        if isinstance(break_on_fail, str):
            self.break_on_fail = break_on_fail.lower() != 'false'
        else:
            self.break_on_fail = bool(break_on_fail)

        self.new_error = True
        self.mutings = []
        self.tempdir = tempfile.mkdtemp()
        self.libraries = dict()
        self.log_messages = []
        self.messages = []
        self.indent = 0
        self.test_phase = None
        self.test_history = []
        self.setup_history = []
        self.teardown_history = []

    def debug(self, keyword=None):
        main = Tk()
        keyword_history = [['### Suite Setup ###']]
        keyword_history += self.setup_history
        if self.test_history:
            keyword_history.append(['### Test Case ###'])
            keyword_history += self.test_history
        if self.teardown_history:
            keyword_history.append(['### Suite Teardown ###'])
            keyword_history += self.teardown_history
        DebuggerGui(main, self.libraries, keyword, '\n'.join(self.log_messages), keyword_history)
        main.mainloop()

    def start_suite(self, name, attrs):
        self.setup_history = []
        self.indent = 0
        self.test_phase = _SUITE_SETUP

    def start_test(self, name, attrs):
        self.test_history = []
        self.indent = 0
        self.test_phase = _TEST_CASE

    def start_keyword(self, name, attrs):
        self.log_messages = []
        self.indent = self.indent + 2
        command = [' ' * self.indent, attrs["kwname"], *attrs['args']]
        if self.test_phase == _SUITE_SETUP:
            self.setup_history.append(command)
        elif self.test_phase == _TEST_CASE:
            self.test_history.append(command)
        else:
            self.teardown_history.append(command)
        if attrs['kwname'] in muting_keywords:
            self.mutings.append(attrs['kwname'])
        if attrs['kwname'].upper() in ['DEBUG', 'BREAK']:
            if len(attrs['args']) == 1:
                attrs['kwname'] = attrs['args'][0]
            if len(attrs['args']) > 1:
                attrs['args'] = attrs['args'][1:]
            self.debug(attrs)
        self.new_error = True

    def end_keyword(self, name, attrs):
        if self.mutings and attrs['kwname'] == self.mutings[-1]:
            self.mutings.pop()
        self.indent = self.indent - 2
        if attrs['status'] == 'FAIL' and self.break_on_fail and self.new_error and not self.mutings:
            self.debug(attrs)
        self.new_error = False

    def end_test(self, name, attrs):
        self.test_phase = _SUITE_TEARDOWN
        self.indent = 0

    def end_suite(self, name, attrs):
        self.teardown_history = []
        self.indent = 0

    def log_message(self, message):
        self.log_messages.append(f'{message["level"]}: {message["message"]}')

    def message(self, message):
        self.messages.append(message)

    def library_import(self, name, attrs):
        self._analyse_import(name, attrs, True)

    def resource_import(self, name, attrs):
        self._analyse_import(name, attrs, False)

    def _analyse_import(self, name, attrs, is_library: bool):
        if is_library:
            libdoc = LibraryDocumentation(name)
        else:
            libdoc = LibraryDocumentation(attrs['source'])
        library = {'name': libdoc.name, 'version': libdoc.version, 'keywords': []}
        for kw in libdoc.keywords:
            if is_RF_4:
                keyword = {'name': kw.name, 'args': [str(arg) for arg in kw.args], 'doc': kw.doc}
            else:
                keyword = {'name': kw.name, 'args': kw.args, 'doc': kw.doc}
            library['keywords'].append(keyword)
        self.libraries[library['name']] = library
