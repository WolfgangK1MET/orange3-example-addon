import Orange

from Orange.data import Table, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import TimeVariable
from Orange.widgets import gui
from Orange.widgets.utils.itemmodels import DomainModel
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import dateutil.parser
import matplotlib.dates as mdates

from AnyQt.QtCore import Qt
from PyQt4 import QtGui
import pandas as pd
from matplotlib import pyplot as plt
from pylab import rcParams
import sys
import time
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
import numpy as np



class OWSeabornTest(OWWidget,QtWidgets.QMainWindow):
    name = "Seaborn Test"
    icon = "icons/oweasyplot.svg"
    want_main_area = True
    
    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        selected = Output("Selected Data", Orange.data.Table)
        
    class Error(OWWidget.Error):
        pass
        
    class Warning(OWWidget.Warning):
        empty_data = Msg("There is no data to show.")
        
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(static_canvas)
        self.addToolBar(NavigationToolbar(static_canvas, self))

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(dynamic_canvas, self))

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()

    @Inputs.data
    def set_input_data(self, data):
        self.__input_data = data
        

        
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("HOA_ADMIN_HOA_DRUCK.csv")
    
    a = QApplication([])
    df = OWSeabornTest()

    df.set_input_data(table)
    
    df.show()
    a.exec()
