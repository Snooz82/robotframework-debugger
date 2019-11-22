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

from tkinter import *
import tkinter.ttk as ttk
import tempfile
import os
import json
from copy import deepcopy
from xml.dom import minidom
from robot.libraries.BuiltIn import BuiltIn
from robot.libdoc import libdoc
from robot.errors import DataError
from tkinterhtml import HtmlFrame

__version__ = '0.1.0'


class Debugger:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, break_on_fail=False):
        self.break_on_fail = break_on_fail
        self.tempdir = tempfile.mkdtemp()
        self.libraries = dict()
        self.log_messages = list()
        self.messages = list()
        self.history = list()

    def start_suite(self, name, attrs):
        pass

    def start_test(self, name, attrs):
        self.log_messages = list()
        self.messages = list()
        self.history = list()

    def start_keyword(self, name, attrs):
        command = attrs["args"]
        command.insert(0, attrs["kwname"])
        self.history.append(command)

    def end_keyword(self, name, attrs):
        if attrs['status'] != 'PASS' and self.break_on_fail:
            self.debug(attrs)

    def debug(self, attrs=None):
        main = Tk()
        Toplevel(main, self.libraries, attrs, self.history)
        main.mainloop()

    def end_test(self, name, attrs):
        pass

    def end_suite(self, name, attrs):
        pass

    def log_message(self, message):
        self.log_messages.append(message)

    def message(self, message):
        self.messages.append(message)

    def library_import(self, name, attrs):
        self._analyse_import(name, attrs, True)

    def resource_import(self, name, attrs):
        self._analyse_import(name, attrs, False)

    def _analyse_import(self, name, attrs, is_library:bool):
        outfile = f'{self.tempdir}/{name}.xml'
        if is_library:
            libdoc(name, outfile, format='XML:HTML')
        else:
            libdoc(attrs['source'], outfile, format='XML:HTML')
        library = LibDocParser().parse_libdoc_xml(outfile)
        if library:
            self.libraries[library['name']] = library
        os.remove(outfile)


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


class Toplevel:

    def __init__(self, top=None, libraries=None, failed_kw=None, history=None):
        """This class configures and populates the toplevel window.
           top is the toplevel containing window."""

        _all_libraries_alias = '-- ALL IMPORTS --'

        self.top = top
        self.libraries = self.get_libraries_from_list(_all_libraries_alias, libraries)
        self.library_names = list(self.libraries.keys())
        if isinstance(failed_kw, dict):
            self.failed_Command = f'{failed_kw["kwname"]}    ' \
                                  f'{"    ".join(failed_kw["args"])}'
        else:
            self.failed_Command = ''
        self.history = history
        self.keyword_names = list()
        self.eventlist = list()
        self.command_value = StringVar()
        self.label_value = StringVar()
        self.combobox_library_value = StringVar()
        self.variable_name_value = StringVar()
        self.variable_value_value = StringVar()
        self.option_filter_keyword = BooleanVar()
        self.option_add_default_param = BooleanVar()

        self.menu_bar = None
        self.config_menu_bar()

        self.file_menu = None
        self.option_menu = None

        self.MainFrame = None
        self.config_main_frame()

        self.EntryCommand = None
        self.ButtonExecute = None
        self.LabelExecutionResult = None
        self.config_execute_button()
        self.config_command_entry_field()
        self.config_execution_result_label()

        self.TNotebook = None
        self.TabKeywords = None

        self.ComboboxLibrary = None
        self.ListboxKeywordsFrame = None
        self.ListboxKeywords = None
        self.ListboxKeywordsScrollBar = None
        self.Html_Frame = None
        self.TabHistory = None
        self.ListboxHistory = None
        self.TabVariables = None
        self.ListboxVariables = None
        self.ListboxVariablesScrollBar = None
        self.VariableFrame = None
        self.EntryVariableName = None
        self.EntryVariableValue = None
        self.ButtonSetVariable = None
        self.config_notebook()

        self.top.title("Robot Framework Debugger")
        self.top.wm_geometry("1000x600")
        self.top.minsize(400, 150)
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)


    @staticmethod
    def get_libraries_from_list(all_libraries_alias, libraries):
        if isinstance(libraries, dict):
            all_libs = dict()
            all_libs[all_libraries_alias] = dict()
            all_libs[all_libraries_alias]['name'] = all_libraries_alias
            all_libs[all_libraries_alias]['version'] = ''
            all_libs[all_libraries_alias]['keywords'] = list()
            for library in libraries:
                for keyword in libraries[library]['keywords']:
                    unique_keyword = deepcopy(keyword)
                    unique_keyword['name'] = f'{libraries[library]["name"]}.{keyword["name"]}'
                    all_libs[all_libraries_alias]['keywords'].append(unique_keyword)
            return {**all_libs, **libraries}
        else:
            return list()

    def config_menu_bar(self):
        self.menu_bar = Menu(self.top)
        self.top.configure(menu=self.menu_bar)
        self.file_menu = Menu(self.top, tearoff=0)
        self.menu_bar.add_cascade(menu=self.file_menu,
                                  compound="left",
                                  label="File")
        self.file_menu.add_command(accelerator="CRTL + S",
                                   label="Save History")
        self.option_menu = Menu(self.top, tearoff=0)
        self.menu_bar.add_cascade(menu=self.option_menu,
                                  compound="left",
                                  label="Options")
        self.option_menu.add_checkbutton(variable=self.option_filter_keyword,
                                         onvalue=True, offvalue=False,
                                         label="Filter Keyword List")
        self.option_menu.add_checkbutton(variable=self.option_add_default_param,
                                         onvalue=True, offvalue=False,
                                         label="Add Default Parameter")
        self.option_filter_keyword.set(True)

    def config_main_frame(self):
        self.MainFrame = Frame(self.top)
        self.MainFrame.grid(column=0, row=0, sticky=N+S+E+W)
        self.MainFrame.columnconfigure(1, weight=1)
        self.MainFrame.rowconfigure(8, weight=1)

    def config_command_entry_field(self):
        self.EntryCommand = ttk.Entry(self.MainFrame)
        self.EntryCommand.grid(row=0, column=0, columnspan=7, sticky=N+W+E)
        validate_command = (self.EntryCommand.register(self.validate_command_entry),
                            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.EntryCommand.configure(textvariable=self.command_value,
                                    font="TkFixedFont",
                                    validate="key",
                                    validatecommand=validate_command)
        self.EntryCommand.bind('<Return>', self.execute_command)
        self.EntryCommand.bind('<Control-space>', self.set_focus_to_keyword_list)
        self.EntryCommand.bind('<Escape>', self.clear_keyword_filter)
        self.EntryCommand.bind('<Tab>', self.select_next_arg)
        self.command_value.set(self.failed_Command)

    def config_execute_button(self):
        self.ButtonExecute = ttk.Button(self.MainFrame)
        self.ButtonExecute.grid(row=0, column=7, columnspan=1, sticky=W)
        self.ButtonExecute.configure(text='''Execute''',
                                     command=self.execute_command)

    def config_execution_result_label(self):
        self.LabelExecutionResult = ttk.Label(self.MainFrame)
        self.LabelExecutionResult.grid(row=1, column=1, sticky=W)
        self.LabelExecutionResult.configure(text='''FAIL''',
                                            font="TkFixedFont",
                                            textvariable=self.label_value)

    def config_notebook(self):
        self.TNotebook = ttk.Notebook(self.MainFrame)
        self.TNotebook.grid(row=2, column=0, columnspan=8, rowspan=10, sticky=N+W+S+E)
        self.TNotebook.configure(takefocus="")
        self.config_keywords_tab()
        self.TNotebook.add(self.TabKeywords, padding=3)
        self.TNotebook.tab(0,
                           text="Keywords",
                           compound="left",
                           underline="-1")
        self.config_history_tab()
        self.TNotebook.add(self.TabHistory, padding=3)
        self.TNotebook.tab(1,
                           text="History",
                           compound="left",
                           underline="-1")
        self.config_variables_tab()
        self.TNotebook.add(self.TabVariables, padding=3)
        self.TNotebook.tab(2,
                           text="Variables",
                           compound="left",
                           underline="-1")

    def config_keywords_tab(self):
        self.TabKeywords = ttk.Frame(self.TNotebook)
        self.TabKeywords.columnconfigure(0, weight=1, minsize=200)
        self.TabKeywords.rowconfigure(1, weight=1)
        self.config_library_combobox()
        self.config_keyword_listbox()
        self.config_documentation_frame()

    def config_library_combobox(self):
        self.ComboboxLibrary = ttk.Combobox(self.TabKeywords)
        self.ComboboxLibrary.grid(row=0, column=0, sticky=N+E+S+W)
        self.ComboboxLibrary.configure(textvariable=self.combobox_library_value,
                                       takefocus="",
                                       state="readonly")
        self.ComboboxLibrary.bind("<<ComboboxSelected>>",
                                  self.select_library_command)
        self.ComboboxLibrary['values'] = self.library_names
        self.combobox_library_value.set(self.library_names[0])

    def config_keyword_listbox(self):
        self.ListboxKeywordsFrame = Frame(self.TabKeywords)
        self.ListboxKeywordsFrame.grid(row=1, column=0, sticky=N+E+S+W)
        self.ListboxKeywords = Listbox(self.ListboxKeywordsFrame)
        self.ListboxKeywordsScrollBar = Scrollbar(self.ListboxKeywordsFrame)
        self.ListboxKeywords.pack(side=LEFT, fill='both', expand=1, anchor='sw')
        self.ListboxKeywordsScrollBar.pack(side=LEFT, fill='y', anchor='se')
        self.ListboxKeywords.config(font="TkFixedFont",
                                    yscrollcommand=self.ListboxKeywordsScrollBar.set)
        self.ListboxKeywordsScrollBar.config(command=self.ListboxKeywords.yview)
        self.ListboxKeywords.bind('<Double-Button-1>',
                                  self.select_keyword_command)
        self.ListboxKeywords.bind('<<ListboxSelect>>',
                                  self.click_keyword_command)
        self.ListboxKeywords.bind('<FocusIn>',
                                  self.click_keyword_command)
        self.ListboxKeywords.bind('<Return>',
                                  self.select_keyword_command)
        self.ListboxKeywords.bind('<Control-Return>',
                                  self.select_keyword_command)
        self.ListboxKeywords.bind('<Escape>',
                                  self.clear_keyword_filter)
        self.select_library_command()

    def config_documentation_frame(self):
        self.Html_Frame = HtmlFrame(self.TabKeywords,
                                    vertical_scrollbar="auto",
                                    horizontal_scrollbar="auto",
                                    width=500)
        self.Html_Frame.grid_propagate(0)
        self.Html_Frame.grid(row=0, column=1, rowspan=2, sticky=N+E+S)
        self.Html_Frame.set_content(f"<html><body>--</body></html>")

    def config_history_tab(self):
        self.TabHistory = ttk.Frame(self.TNotebook)
        self.TabHistory.columnconfigure(0, weight=1)
        self.TabHistory.rowconfigure(0, weight=1)
        self.config_history_listbox()

    def config_history_listbox(self):
        self.ListboxHistory = Listbox(self.TabHistory)
        self.ListboxHistory.grid(column=0, row=0, sticky=N+S+E+W)
        self.ListboxHistory.configure(font="TkFixedFont",
                                      selectmode=EXTENDED)
        self.ListboxHistory.bind('<Double-Button-1>',
                                 self.select_history_command)
        for commands in self.history:
            self.ListboxHistory.insert(0, '    '.join(commands))

    def config_variables_tab(self):
        self.TabVariables = ttk.Frame(self.TNotebook)
        self.TabVariables.columnconfigure(0, weight=1)
        self.TabVariables.columnconfigure(1, weight=4)
        self.TabVariables.rowconfigure(1, weight=1)
        self.config_set_variables_button()
        self.config_variables_name_field()
        self.config_variables_value_field()
        self.config_variables_listbox()

    def config_set_variables_button(self):
        self.ButtonSetVariable = ttk.Button(self.TabVariables)
        self.ButtonSetVariable.grid(row=0, column=2, sticky=E)
        self.ButtonSetVariable.configure(text='''Set Variable''',
                                         command=self.set_variable)

    def config_variables_name_field(self):
        self.EntryVariableName = ttk.Entry(self.TabVariables)
        self.EntryVariableName.grid(row=0, column=0, sticky=W+E)
        self.EntryVariableName.configure(textvariable=self.variable_name_value,
                                         font="TkFixedFont",
                                         validate="key")
        self.EntryVariableName.bind('<Return>', self.set_variable)

    def config_variables_value_field(self):
        self.EntryVariableValue = ttk.Entry(self.TabVariables)
        self.EntryVariableValue.grid(row=0, column=1, sticky=W+E)
        self.EntryVariableValue.configure(textvariable=self.variable_value_value,
                                          font="TkFixedFont",
                                          validate="key")
        self.EntryVariableValue.bind('<Return>', self.set_variable)
        self.EntryVariableValue.bind('<Tab>', self.select_next_arg)

    def config_variables_listbox(self):
        self.VariableFrame = ttk.Frame(self.TabVariables)
        self.VariableFrame.grid(row=1, column=0, columnspan=6, rowspan=6, sticky=W+E+S+N)
        self.ListboxVariables = Listbox(self.VariableFrame)
        self.ListboxVariablesScrollBar = Scrollbar(self.VariableFrame)
        self.ListboxVariables.pack(side=LEFT,
                                   fill='both',
                                   expand=1,
                                   anchor='sw')
        self.ListboxVariablesScrollBar.pack(side=LEFT,
                                            fill='y',
                                            anchor='se')
        self.ListboxVariables.config(font="TkFixedFont",
                                     yscrollcommand=self.ListboxVariablesScrollBar.set)
        self.ListboxVariablesScrollBar.config(command=self.ListboxVariables.yview)
        self.ListboxVariables.bind('<F5>', self.update_variables_list)
        self.ListboxVariables.bind('<<ListboxSelect>>', self.select_variable)
        self.update_variables_list()

    def set_variable(self, event=None):
        name = self.variable_name_value.get()
        if not (name[0] in '@$&' and name[1] == '{' and name[-1] == '}'):
            name = f'${{{name}}}'
            self.variable_name_value.set(name)
        value = self.variable_value_value.get().strip()
        value = self._try_json_var(value)
        try:
            value = self._try_str_var(name, value)
            self._try_list_var(name, value)
            name = self._try_dict_var(name, value)
            var = BuiltIn().get_variable_value(name)
            self.label_value.set(f'{name} => {var}')
        except DataError as e:
            self.label_value.set(e)
        self.update_variables_list()

    @staticmethod
    def _try_dict_var(name, value):
        if isinstance(value, dict) and name[0] in '$&':
            name = f'${name[1:]}'
            BuiltIn().set_test_variable(name, value)
        return name

    @staticmethod
    def _try_list_var(name, value):
        if isinstance(value, list):
            if name[0] in '@&':
                BuiltIn().set_test_variable(name, *value)
            elif name[0] == '$':
                BuiltIn().set_test_variable(name, value)

    @staticmethod
    def _try_str_var(name, value):
        if isinstance(value, str):
            if '  ' in value or name[0] == '@':
                value = [v.strip()
                         for v in value.split('  ')
                         if v.strip() != '']
            elif name[0] in '$&':
                BuiltIn().set_test_variable(name, value)
        return value

    @staticmethod
    def _try_json_var(value):
        try:
            value = json.loads(value.replace("'", '"'))
        except ValueError:
            pass
        return value

    def _get_command(self):
        command = self.EntryCommand.get()
        commands = command.split('  ')
        return [c.strip() for c in commands if c != '']

    def execute_command(self, event=None):
        commands = self._get_command()
        try:
            self.LabelExecutionResult. \
                configure(text=f'Sent:  {"    ".join(commands)}')
            return_value = BuiltIn().run_keyword(*commands)
            if isinstance(return_value, str):
                return_value = repr(return_value)[1:-1]
            self.label_value.set(f'${{RETURN_VALUE}} => {return_value}')
            BuiltIn().set_test_variable('${RETURN_VALUE}', return_value)
            self.update_variables_list()
            self.ListboxHistory.insert(0, '    '.join(commands))
        except Exception as e:
            self.label_value.set(f'FAIL: {str(e)}')

    def select_history_command(self, event=None):
        command = self.ListboxHistory.get(ACTIVE)
        self.command_value.set(command)
        self.EntryCommand.update()

    def select_keyword_command(self, event=None):
        keyword_dict = self.get_keyword_from_library(self.combobox_library_value.get(),
                                                     self.ListboxKeywords.get(ACTIVE))
        if keyword_dict:
            args = keyword_dict["args"]
            keyword = keyword_dict["name"]
            if self.is_modifier_used(event.state, 'Control') == self.option_add_default_param.get():
                args = [x for x in args if '=' not in x]
            self.command_value.set(f'{keyword}    {"    ".join(args)}')
            self.EntryCommand.focus_set()
            if len(args) > 0:
                arg1_start = len(keyword) + 4
                arg1_end = arg1_start + len(args[0])
                self.EntryCommand.selection_range(arg1_start, arg1_end)
                self.EntryCommand.icursor(arg1_start)
            else:
                self.EntryCommand.icursor(len(keyword))
            self.EntryCommand.update()

    def select_library_command(self, event=None):
        selected_lib = self.combobox_library_value.get()
        self.ListboxKeywords.delete(0, END)
        self.keyword_names = list()
        if self.libraries:
            for keyword in dict(self.libraries[selected_lib])['keywords']:
                self.keyword_names.append(keyword['name'])
                self.ListboxKeywords.insert(END, keyword['name'])

    def update_variables_list(self, event=None):
        self.ListboxVariables.delete(0, END)
        variables = BuiltIn().get_variables()
        longest_var_name = ''
        for variable in variables:
            if len(variable) > len(longest_var_name):
                longest_var_name = variable
        for variable in variables:
            i = len(longest_var_name) - len(variable)
            self.ListboxVariables.insert(END,
                                         f'{variable}=    {i*" "}{str(variables[variable])}')

    def select_variable(self, event=None):
        if event.x_root < 0:
            widget = event.widget
            selected_var = widget.get(widget.curselection()).split('=', 1)
            self.variable_name_value.set(selected_var[0])
            if len(selected_var) == 2:
                printable = repr(selected_var[1].strip())
                self.variable_value_value.set(printable[1:-1])

    def click_keyword_command(self, event=None):
        if isinstance(event.x_root, str) or event.x_root < 0:
            try:
                name = self.ListboxKeywords.get(self.ListboxKeywords.curselection()[0])
                keyword = self.get_keyword_from_library(self.combobox_library_value.get(), name)
                self.Html_Frame.set_content(
                    f"""
                    <html>
                    <body>
                    <h3>Keyword:</h3>
                    {keyword['name']}
                    <h3>Arguments:</h3>
                    {'<br/>'.join(keyword['args'])}
                    <h3>Documentation:</h3>
                    {keyword['doc']}
                    </body>
                    </html>
                    """)
            except Exception as e:
                print(e)

    def get_keyword_from_library(self, library, name):
        selected_lib = self.libraries[library]
        for keyword in dict(selected_lib)['keywords']:
            if keyword['name'] == name:
                return keyword

    def validate_command_entry(self, d, i, P, s, S, v, V, W):
        if hasattr(self, 'ListboxKeywords') and self.option_filter_keyword.get():
            try:
                keyword_entry = str(P).split('  ', 1)
                keyword_entry = keyword_entry[0].strip()
                self.ListboxKeywords.delete(0, END)
                for keyword in self.keyword_names:
                    if keyword_entry.lower() in keyword.lower():
                        self.ListboxKeywords.insert(END, keyword)
            except Exception as e:
                print(e)
        else:
            self.ListboxKeywords.delete(0, END)
            for keyword in self.keyword_names:
                self.ListboxKeywords.insert(END, keyword)
        return True

    def set_focus_to_keyword_list(self, event=None):
        self.ListboxKeywords.focus_set()
        self.ListboxKeywords.selection_set(0)

    def clear_keyword_filter(self, event=None):
        self.EntryCommand.delete(0, END)
        self.EntryCommand.focus_set()
        self.EntryCommand.icursor(0)

    def select_next_arg(self, event=None):
        if self.is_modifier_used(event.state, 'Control'):
            return
        entry = event.widget
        if self.is_modifier_used(event.state, 'Shift'):
            return self._move_backward(entry)
        else:
            return self._move_forward(entry)

    def _move_backward(self, entry):
        text = entry.get()
        index = entry.index(INSERT)
        if not (text[index:index + 2] == '  '
                or text[index - 1:index + 1] == '  '
                or text[index - 2:index] == '  '):
            index = text[:index].rfind('  ') + len('  ')
        arg_end = index - (len(text[:index]) - len(text[:index].rstrip()))
        space_index = text[:arg_end].rfind('  ')
        if space_index == -1:
            arg_start = 0
        else:
            next_space = len(text[:arg_end]) - (space_index + len('  '))
            arg_start = arg_end - next_space
        if (entry.selection_present()
                and entry.index(SEL_FIRST) == arg_start
                and entry.index(SEL_LAST) == arg_end):
            entry.icursor(arg_start - 1)
            entry.selection_clear()
            self._move_backward(entry)
        else:
            entry.selection_range(arg_start, arg_end)
            entry.icursor(arg_start)
        return "break"

    def _move_forward(self, entry):
        text = entry.get()
        index = entry.index(INSERT)
        if not (text[index:index + 2] == '  '
                or text[index - 1:index + 1] == '  '
                or text[index - 2:index] == '  '):
            if text[index:].find('  ') == -1:
                entry.delete(0, END)
                entry.insert(0, f'{text}    ')
                entry.icursor(len(entry.get()))
                return "break"
            index = index + text[index:].find('  ')
        arg_start = index + (len(text[index:]) - len(text[index:].lstrip()))
        next_space = text[arg_start:].find('  ')
        if next_space == -1:
            arg_end = len(text)
        else:
            arg_end = arg_start + next_space
        if (entry.selection_present()
                and entry.index(SEL_FIRST) == arg_start
                and entry.index(SEL_LAST) == arg_end):
            entry.icursor(arg_start + 1)
            entry.selection_clear()
            self._move_forward(entry)
        else:
            entry.selection_range(arg_start, arg_end)
            entry.icursor(arg_start)
        return "break"

    @staticmethod
    def is_modifier_used(state, modifier):
        if isinstance(state, int):
            mods = ('Shift', 'Lock', 'Control',
                    'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Mod5',
                    'Button1', 'Button2', 'Button3', 'Button4', 'Button5')
            s = []
            for i, n in enumerate(mods):
                if state & (1 << i):
                    s.append(n)
            state = state & ~((1 << len(mods)) - 1)
            if state or not s:
                s.append(hex(state))
            if modifier in s:
                return True
        return False


if __name__ == '__main__':
    root = Tk()
    Toplevel(root)
    root.mainloop()
