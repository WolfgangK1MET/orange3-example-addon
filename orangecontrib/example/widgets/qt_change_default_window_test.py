import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import TimeVariable
from Orange.widgets import gui

from AnyQt.QtCore import Qt
from PyQt4 import QtGui

class Second(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)
        
        
class TestQtWindow(OWWidget):
    name = "qt-window-test"
    description = "A widget for easy plots with matplotlib"
    icon = "icons/oweasyplot.svg"
    
    def __init__(self):
        self.second_window = Second(self)
        self.second_window.show()

    def show(self):
        # Wird leider nicht in Orange aufgerufen ...
        super().show()
        self.hide()
        self.second_window = Second(self)
        self.second_window.show()

    def exec_(self):
        # Wird leider auch nicht aufgerufen
        self.hide()
        self.second_window = Second(self)
        self.second_window.show()
        
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("WK1_20200201.csv")
    
    a = QApplication([])
    df = TestQtWindow()


    df.show()
    a.exec()