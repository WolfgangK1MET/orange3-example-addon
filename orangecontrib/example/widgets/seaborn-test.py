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

from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import seaborn as sns

tips = sns.load_dataset("tips")


def seabornplot():
    g = sns.FacetGrid(tips, col="sex", hue="time", palette="Set1",hue_order=["Dinner", "Lunch"])
    g.map(plt.scatter, "total_bill", "tip", edgecolor="w")
    return g.fig


class OWSeabornTest(OWWidget,QtWidgets.QMainWindow):
    name = "Matplot - test"
    description = "A widget for easy plots with matplotlib"
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
        self.main_widget = QtGui.QWidget(self)

        self.graph = Figure()
        self.ax1 = self.graph.add_subplot(121)
        self.ax2 = self.graph.add_subplot(122, sharex=self.ax1, sharey=self.ax1)
        self.axes=[self.ax1, self.ax2]
        self.graph = FigureCanvas(self.graph)

        self.graph.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.graph.updateGeometry()
        
        self.dropdown1 = QtGui.QComboBox()
        self.dropdown1.addItems(["sex", "time", "smoker"])
        self.dropdown2 = QtGui.QComboBox()
        self.dropdown2.addItems(["sex", "time", "smoker", "day"])
        self.dropdown2.setCurrentIndex(2)
        
        self.dropdown1.currentIndexChanged.connect(self.update)
        self.dropdown2.currentIndexChanged.connect(self.update)

        self.label = QtGui.QLabel("A plot:")


        self.show()
        self.update()

    @Inputs.data
    def set_input_data(self, data):
        self.__input_data = data
        
    def update(self):

        colors=["b", "r", "g", "y", "k", "c"]
        self.ax1.clear()
        self.ax2.clear()
        cat1 = self.dropdown1.currentText()
        cat2 = self.dropdown2.currentText()
        print (cat1, cat2)

        for i, value in enumerate(tips[cat1].unique()):
            print ("value ", value)
            df = tips.loc[tips[cat1] == value]
            self.axes[i].set_title(cat1 + ": " + value)
            for j, value2 in enumerate(df[cat2].unique()):
                print ("value2 ", value2)
                df.loc[ tips[cat2] == value2 ].plot(kind="scatter", x="total_bill", y="tip", 
                                                ax=self.axes[i], c=colors[j], label=value2)
        self.axes[i].legend()   
        self.graph.canvas.draw_idle()
        

        
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("HOA_ADMIN_HOA_DRUCK.csv")
    
    a = QApplication([])
    df = OWSeabornTest()

    df.set_input_data(table)
    
    df.show()
    a.exec()
