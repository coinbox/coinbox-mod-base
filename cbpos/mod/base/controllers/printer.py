from PySide import QtGui, QtCore

import cbpos

logger = cbpos.get_logger(__name__)

class PrinterManager(object):
    def __init__(self):
        pass
    
    def prompt(self, name):
        qprinter = QtGui.QPrinter()
        print_dialog = QtGui.QPrintDialog(qprinter)
        if print_dialog.exec_() == QtGui.QDialog.Accepted:
            
            page_dialog = QtGui.QPageSetupDialog(qprinter)
            page_dialog.exec_()
            
            qprinter.setPageMargins(0, 0, 0, 0, QtGui.QPrinter.Inch)
            
            return self.save(name, qprinter)
    
    def save(self, name, qprinter):
        # TODO: save the configuration of the printer
        return Printer(name, qprinter)
    
    def load(self, name):
        # TODO: load the configuration of the printer
        return Printer(name, QtGui.QPrinter())

class Printer(object):
    def __init__(self, name, qprinter):
        self.qprinter = qprinter
        self.name = name
    
    def preview(self, job):
        preview = QtGui.QPrintPreviewDialog(self.qprinter)
        preview.paintRequested.connect(job.handler)
        preview.exec_()
    
    def execute(self, job):
        job.handler(self.qprinter)

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
