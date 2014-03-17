
import geany
import sys
import pep8


def get_pep8_errors(filename, **pep8_options):
    """Execute pep8 via python method calls."""
    class QuietReport(pep8.BaseReport):

        """Version of checker that does not print."""

        def __init__(self, options):
            super(QuietReport, self).__init__(options)
            self.__full_error_results = []

        def error(self, line_number, offset, text, _):
            """Collect errors."""
            code = super(QuietReport, self).error(line_number, offset, text, _)
            if code:
                self.__full_error_results.append(
                    {'id': code,
                     'line': line_number,
                     'column': offset + 1,
                     'info': text})

        def full_error_results(self):
            """Return error results in detail.

            Results are in the form of a list of dictionaries. Each
            dictionary contains 'id', 'line', 'column', and 'info'.

            """
            return self.__full_error_results

    checker = pep8.Checker(filename, reporter=QuietReport, **pep8_options)
    checker.check_all()
    return checker.report.full_error_results()


class Pep8Plugin(geany.Plugin):

    __plugin_name__ = "PEP-8 Support"
    __plugin_description__ = "Highlights PEP-8 errors in python files."
    __plugin_version__ = "0.2"
    __plugin_author__ = "Nitori Kawashiro <nitori@cock.li>"

    def __init__(self):
        geany.Plugin.__init__(self)
        geany.signals.connect('document-save', self.check_pep8_errors)
        geany.signals.connect('document-open', self.check_pep8_errors)
        self.error_format = '{filename}:{line}:{column} {info}'

    def cleanup(self):
        pass

    def check_pep8_errors(self, sigman, doc):
        if doc.file_name.endswith('.py'):
            results = get_pep8_errors(doc.file_name)
            doc.editor.indicator_clear(geany.editor.INDICATOR_ERROR)
            geany.msgwindow.clear_tab(geany.msgwindow.TAB_MESSAGE)
            if results:
                geany.msgwindow.switch_tab(geany.msgwindow.TAB_MESSAGE)
                for error in results:
                    error['filename'] = doc.file_name
                    geany.msgwindow.msg_add(
                        self.error_format.format(**error),
                        geany.msgwindow.COLOR_DARK_RED, error['line'], doc)
                    doc.editor.indicator_set_on_line(
                        geany.editor.INDICATOR_ERROR, error['line']-1)
            else:
                geany.msgwindow.switch_tab(geany.msgwindow.TAB_STATUS)
