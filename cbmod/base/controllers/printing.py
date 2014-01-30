from PySide import QtGui, QtCore

import cbpos

logger = cbpos.get_logger(__name__)

class InvalidPrinterFunction(ValueError):
    pass

class InvalidPrinterName(ValueError):
    pass

class PrinterManager(object):
    
    NoPrinter = -1
    
    def __init__(self):
        pass
    
    def prompt_printer(self, name, printer=None):
        """
        Opens a dialog to let the user configure a printer.
        """
        if printer is None:
            qprinter = QtGui.QPrinter()
        else:
            # TODO: On Windows (at least), the copy count is not showing in the dialog
            # and I suspect others too not to update...
            qprinter = QtGui.QPrinter(printer.qprinter)
        
        print_dialog = QtGui.QPrintDialog(qprinter)
        if print_dialog.exec_() == QtGui.QDialog.Accepted:
            
            page_dialog = QtGui.QPageSetupDialog(qprinter)
            page_dialog.exec_()
            
            qprinter.setPageMargins(0, 0, 0, 0, QtGui.QPrinter.Inch)
            
            return Printer(name, qprinter)
    
    def select_printer(self):
        """
        Opens a dialog to let the user select
        one of the configured printers.
        """
        printer_names = self.get_printer_names()
        
        item, ok = QtGui.QInputDialog.getItem(cbpos.ui.window, cbpos.tr.base_("Select Printer"),
                                     cbpos.tr.base_("Choose a printer for this job:"),
                                     printer_names, -1, False)
        
        if ok:
            return self.load_printer(item)
        else:
            raise InvalidPrinterName, 'User did not select'
    
    def save_printer(self, printer):
        """
        Save the printer configuration under this `name`.
        """
        cbpos.config['printing', 'p.'+printer.name] = printer.serialized()
        return printer
    
    def remove_printer(self, printer):
        cbpos.config['printing', 'p.'+printer.name] = None
    
    def load_printer(self, name):
        """
        Load the printer configuration under this `name`.
        """
        serial = cbpos.config['printing', 'p.'+name]
        if serial is None:
            raise InvalidPrinterName, 'Does not exist'
        
        printer = Printer(name, serial)
        return printer
    
    def get_printer_names(self):
        return [p[2:] for p in cbpos.config['printing'] if p.startswith('p.')]
    
    def register_function(self, function):
        """
        Register this printer function, so that the user can configure
        a printer to use for that function.
        """
        p = cbpos.config['printing', 'f.'+function]
        if p is not None:
            return
        
        cbpos.config['printing', 'f.'+function] = PrinterManager.NoPrinter
    
    def set_function_printer(self, function, printer):
        """
        Set the printer with name `printer_name` to use
        for this function.
        If `printer_name` is None, always ask the user
        to select the printer to use.
        """
        if printer is None:
            cbpos.config['printing', 'f.'+function] = PrinterManager.NoPrinter
        else:
            cbpos.config['printing', 'f.'+function] = printer.name
    
    def get_function_printer(self, function):
        printer = cbpos.config['printing', 'f.'+function]
        if printer == PrinterManager.NoPrinter:
            return None
        elif printer is None:
            raise InvalidPrinterFunction, 'Does not exist'
        else:
            return self.load_printer(printer)
    
    def get_function_printer_name(self, function):
        printer = cbpos.config['printing', 'f.'+function]
        return printer
    
    def get_function_names(self):
        return [f[2:] for f in cbpos.config['printing'] if f.startswith('f.')]
    
    def get_default_printer(self):
        """
        Returns the default printer.
        """
        printer_name = cbpos.config['printing', 'default']
        if printer_name is None:
            return Printer('[default]', QtGui.QPrinter())
        else:
            return self.load_printer(printer_name)
    
    def handle(self, job, function):
        """
        Handle a print job depending on the function and configuration
        of the printers and printer manager.
        """
        if function is None:
            printer = self.get_default_printer()
        else:
            try:
                printer = self.get_function_printer(function)
            except (InvalidPrinterFunction, InvalidPrinterName):
                # Configuration error
                return
            
            if printer is None:
                try:
                    printer = self.select_printer()
                except InvalidPrinterName:
                    # User did not select a printer
                    return
        
        preview = cbpos.config['printing', 'force_preview']
        if preview:
            printer.preview(job)
        else:
            printer.execute(job)

class Printer(object):
    def __init__(self, name, qprinter):
        self.name = name
        if isinstance(qprinter, QtGui.QPrinter):
            self.qprinter = qprinter
        else:
            self.qprinter = self.deserialized(qprinter)
    
    def preview(self, job):
        preview = QtGui.QPrintPreviewDialog(self.qprinter)
        preview.paintRequested.connect(job.handler)
        preview.exec_()
    
    def execute(self, job):
        job.handler(self.qprinter)
    
    def serialized(self):
        qp = self.qprinter
        unit = QtGui.QPrinter.Millimeter
        
        return {'name': qp.printerName(),
                'unit': int(unit),
                
                'orientation': int(qp.orientation()),
                'paper_size': qp.paperSize(unit).toTuple(),
                'resolution': int(qp.resolution()),
                'full_page': qp.fullPage(),
                'copy_count': qp.copyCount(),
                
                'output_format': int(qp.outputFormat()),
                'output_filename': qp.outputFileName(),
                'print_range': int(qp.printRange()),
                'print_from': qp.fromPage(),
                'print_to': qp.toPage(),
                'printer_mode': int(QtGui.QPrinter.HighResolution),
                'color_mode': int(qp.colorMode()),
                'page_order': int(qp.pageOrder()),
                
                'page_margins': qp.getPageMargins(unit),
                
                # X11
                'duplex': int(qp.duplex()),
                'double_side': qp.doubleSidedPrinting(),
                'font_embed': qp.fontEmbeddingEnabled(),
                
                # Windows
                'paper_source': int(qp.paperSource())
            }
        
    def deserialized(self, s):
        qp = QtGui.QPrinter(QtGui.QPrinter.PrinterMode(s['printer_mode']))
        
        unit = QtGui.QPrinter.Unit(s['unit'])
        
        qp.setPrinterName(s['name'])
        
        qp.setOrientation(QtGui.QPrinter.Orientation(s['orientation']))
        qp.setPaperSize(QtCore.QSizeF(*s['paper_size']), unit)
        qp.setResolution(s['resolution'])
        qp.setFullPage(s['full_page'])
        qp.setCopyCount(s['copy_count'])
        
        qp.setOutputFormat(QtGui.QPrinter.OutputFormat(s['output_format']))
        qp.setOutputFileName(s['output_filename'])
        qp.setPrintRange(QtGui.QPrinter.PrintRange(s['print_range']))
        qp.setFromTo(s['print_from'], s['print_to'])
        qp.setColorMode(QtGui.QPrinter.ColorMode(s['color_mode']))
        qp.setPageOrder(QtGui.QPrinter.PageOrder(s['page_order']))
        
        qp.setPageMargins(*(list(s['page_margins'])+[unit]))
        
        qp.setDuplex(QtGui.QPrinter.DuplexMode(s['duplex']))
        qp.setDoubleSidedPrinting(s['double_side'])
        qp.setFontEmbeddingEnabled(s['font_embed'])
        
        qp.setPaperSource(QtGui.QPrinter.PaperSource(s['paper_source']))
        
        return qp

class PrintJob(object):
    def handler(self, qprinter):
        pass

class DocPrintJob(PrintJob):
    header = ""
    content = ""
    footer = ""
    
    def __init__(self):
        self.doc = None
        self.cursor = None
    
    def insert_header(self):
        self.cursor.insertText(self.header)
        self.cursor.insertText("\n\n")
    
    def insert_content(self):
        self.cursor.insertText(content)
    
    def insert_footer(self):
        self.cursor.insertText("\n\n")
        
        footer_fmt = self.cursor.blockFormat()
        footer_fmt.setAlignment(QtCore.Qt.AlignCenter)
        self.cursor.setBlockFormat(footer_fmt)
        
        self.cursor.insertText(self.footer)
    
    def handler(self, qprinter):
        # Create new document
        self.doc = QtGui.QTextDocument()
        self.cursor = QtGui.QTextCursor(self.doc)
        
        # Seek to start
        self.cursor.movePosition(QtGui.QTextCursor.Start)
        
        # Insert header
        self.insert_header()
        
        # Create main frame underneath
        fmt = QtGui.QTextFrameFormat()
        self.main_frame = self.cursor.insertFrame(fmt)
        
        # Seek into main frame
        self.cursor.setPosition(self.main_frame.firstPosition())
        
        # Insert content
        self.insert_content()
        
        # Seek out of main frame
        self.cursor.setPosition(self.main_frame.lastPosition())
        self.cursor.movePosition(QtGui.QTextCursor.NextBlock)
        
        # Seek to end
        self.cursor.movePosition(QtGui.QTextCursor.End)
        
        # Insert footer
        self.insert_footer()
        
        # Print the document
        self.doc.print_(qprinter)

class TablePrintJob(DocPrintJob):
    def __init__(self, data=None, headers=None, footers=None):
        super(TablePrintJob, self).__init__()
        
        self.table_data = data
        self.table_headers = headers
        self.table_footers = footers
    
    def insert_content(self):
        try:
            num_rows = len(self.table_data)
            num_cols = max(len(d) for d in self.table_data)
        except TypeError:
            # table_data is None
            num_rows = 0
            num_cols = 0
        
        try:
            num_cols = max(num_cols, len(self.table_headers))
        except TypeError:
            pass
        
        extra_rows = 0
        if self.table_headers is not None:
            extra_rows += 1
        if self.table_footers is not None:
            extra_rows += 1
        
        table_fmt = QtGui.QTextTableFormat()
        table_fmt.setBorder(0)
        table_fmt.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 100))
        
        header_fmt = QtGui.QTextCharFormat()
        header_fmt.setFontUnderline(False)
        header_fmt.setFontWeight(QtGui.QFont.Black)
        
        footer_fmt = QtGui.QTextCharFormat()
        footer_fmt.setFontUnderline(False)
        footer_fmt.setFontItalic(True)
        
        line_fmt = QtGui.QTextFrameFormat()
        line_fmt.setBorder(1)
        line_fmt.setBorderStyle(QtGui.QTextFrameFormat.BorderStyle_Inset)
        line_fmt.setMargin(0)
        line_fmt.setPadding(0)
        line_fmt.setHeight(QtGui.QTextLength(QtGui.QTextLength.FixedLength, 0))
        line_fmt.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 100))
        line_fmt.setPosition(QtGui.QTextFrameFormat.FloatRight)
        
        def insertLine():
            """
            Simulates a 2-pixel line by adding a frame of height 0
            """
            self.cursor.insertFrame(line_fmt)
            cell_fmt = self.cursor.blockCharFormat()
            font = cell_fmt.font()
            font.setPixelSize(1)
            cell_fmt.setFont(font)
            self.cursor.setBlockCharFormat(cell_fmt)
            self.cursor.movePosition(QtGui.QTextCursor.NextBlock)
        
        # Create the table
        table = self.cursor.insertTable(extra_rows+num_rows, num_cols, table_fmt)
        
        if self.table_headers is not None:
            # Add the headers
            for c, col in enumerate(self.table_headers):
                # Align every cell to the center
                cell_fmt = self.cursor.blockFormat()
                cell_fmt.setAlignment(QtCore.Qt.AlignCenter)
                self.cursor.setBlockFormat(cell_fmt)
                
                self.cursor.insertText(unicode(col), header_fmt)
                
                # Insert a line, to simulate bottom border
                insertLine()
                
                # Seek to the next cell
                self.cursor.movePosition(QtGui.QTextCursor.NextCell)
        
        if self.table_data is not None:
            # Add the data
            for r, row in enumerate(self.table_data):
                for c, col in enumerate(row):
                    # Right align columns with currency values...
                    #cell_fmt = self.cursor.blockFormat()
                    #if c == 2:
                    #    cell_fmt.setAlignment(QtCore.Qt.AlignRight)
                    #self.cursor.setBlockFormat(cell_fmt)
                    
                    self.cursor.insertText(unicode(col))
                    
                    # Seek to the next cell
                    self.cursor.movePosition(QtGui.QTextCursor.NextCell)
        
        if self.table_footers is not None:
            # Add the footers
            for c, col in enumerate(self.table_footers):
                # Insert a line, to simulate top border
                insertLine()
                
                self.cursor.insertText(unicode(col), footer_fmt)
                
                # Seek to the next cell
                self.cursor.movePosition(QtGui.QTextCursor.NextCell)
        
        # Seek out of the table, just in case
        self.cursor.movePosition(QtGui.QTextCursor.NextBlock)

class HTMLPrintJob(DocPrintJob):
    def insert_header(self):
        self.cursor.insertHtml(self.header)
        self.cursor.insertText("\n\n")
    
    def insert_content(self):
        self.cursor.insertHtml(content)
    
    def insert_footer(self):
        self.cursor.insertText("\n\n")
        self.cursor.insertHtml(self.footer)

manager = None

from cbmod.base.controllers import FormController

class PrinterFormController(FormController):
    cls = Printer
    
    def proxy(self, item):
        class ProxyItem(object):
            def __init__(self, p):
                self.display = p.name
                self.printer = p
        return ProxyItem(item)
    
    def fields(self):
        return {"name": (cbpos.tr.base_("Name"), ""),
                "setup": (cbpos.tr.base_("Setup"), None),
                "info": (cbpos.tr.base_("Info"), None),
                "functions": (cbpos.tr.base_("Use for"), []),
                }
    
    def new(self, data=dict()):
        if data['printer'] is None:
            return None
        
        data['printer'].name = data['name']
        manager.save_printer(data['printer'])
        
        return self.proxy(data['printer'])
    
    def delete(self, item):
        manager.remove_printer(item.printer)
    
    def update(self, item, data=dict()):
        
        manager.remove_printer(item.printer)
        
        prev_name = item.printer.name if item is not None else None
        printer = data['printer']
        printer.name = data['name'] if 'name' in data is not None else prev_name
        
        manager.save_printer(printer)
        
        functions = data['functions']
        for f in manager.get_function_names():
            if f in functions:
                manager.set_function_printer(f, printer)
            elif manager.get_function_printer_name(f) == prev_name:
                manager.set_function_printer(f, None)
        
        item.name = printer.name
        item.printer = printer
        return item
    
    def items(self):
        return [self.proxy(manager.load_printer(p)) for p in manager.get_printer_names()]
    
    def getDataFromItem(self, field, item):
        if field == 'name':
            return item.display
        elif field == 'printer':
            return item.printer
        elif field == 'info':
            return item.printer
        elif field == 'functions':
            return [f for f in manager.get_function_names() if manager.get_function_printer_name(f) == item.display]
