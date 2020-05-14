import Orange
import Orange.data

import numpy as np
import scipy as sp

import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget

from datetime import datetime, timezone

from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import QWidget
    
from Orange.data import Table, ContinuousVariable, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui, settings
from Orange.widgets.settings import Setting, ContextSetting
from Orange.widgets.utils.itemmodels import DomainModel

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# class MyWidget(OWDataProjectionWidget):
class MyWidget(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Test WG"
    description = "A widget for tests from Wolfgang"
    icon = "icons/mywidget.svg"
    want_main_area = True
    
    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        selected = Output("Selected Data", Orange.data.Table)

    attr_x = ContextSetting(None)
    attr_y = ContextSetting(None)
    
    def __init__(self):
    # def __init__(self, parent=None, view_box=ViewBox):        
        super().__init__()
        
        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, 
                              sendSelectedValue=True, contentsLength=14)
        self.attr_box = gui.vBox(self.controlArea, True)
        self.infoa = gui.widgetLabel(
            self.attr_box, "No data on input yet, waiting to get something.")
        
        self.btnAdd = gui.button(self.attr_box, self, "Add Axis", 
                                 callback=self.addAxis)

        self.btnAdd.setEnabled(False)

        dmod = DomainModel
        self.xy_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        
        self.cb_attr_x = gui.comboBox(
            self.attr_box, self, "attr_x", label="Axis x:",
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        self.cb_attr_x.setEnabled(False)
        
        self.cb_attr_y = gui.comboBox(
            self.attr_box, self, "attr_y", label="Axis y:",
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        
        gui.rubber(self.attr_box);
        
        self.scaleBox = gui.vBox(self.attr_box, True)
        self.infoa = gui.widgetLabel(self.scaleBox, "Scale Y Data")
        self.scaleBoxBtn = gui.hBox(self.scaleBox, True)
        self.btnMax = gui.button(self.scaleBoxBtn, self, "0 - Max", 
                                 callback=self.max0)        
        self.btnMinMax= gui.button(self.scaleBoxBtn, self, "Fit", 
                                 callback=self.minmax)
        self.scaleBox.setEnabled(False)
        
        box = gui.vBox(self.mainArea, True, margin=0)        
        # self.graph = pg.PlotWidget(self)
        # box.layout().addWidget(self.graph)
        # self.graph.plot(x, y, name = "DATA", symbol='o', symbolSize=20)
    
        # self.graph.setLabel('left', 'Y-Data', color='red', size=30)
        # self.graph.setLabel('bottom', 'X-Data (e.g. Time)', color='red', size=30)
        # self.graph.addLegend()
        # self.graph.showGrid(x=True, y=True)
    
        self.graph = MatplotlibWidget()
        box.layout().addWidget(self.graph)
        # self.graph.getFigure().plot(x,y)
        self.subplot = self.graph.getFigure().add_subplot()
        # self.subplot.plot(x,y)
        
        self.show()
        
    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.data = dataset
            self.infoa.setText("%d instances in input data set" % len(dataset))
            self.check_data()
            self.init_attr_values()
        else:
            self.Outputs.selected.send(None)

    def addAxis(self, index):
        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, 
                              sendSelectedValue=True, contentsLength=14)
        self.cb_attr_y = gui.comboBox(
            self.attr_box, self, "attr_new", label="Axis %i new:" %index,
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        self.cb_attr_y.setEnabled(False)

    def max0(self):
        self.subplot.autoscale(enable=False, axis='y')
        self.subplot.set_ymargin(0, max(self.subplot.Y))
        
    def minmax(self):
        self.subplot.autoscale(enable=True, axis='y')

    def check_data(self):
        # super().check_data()
        
        if self.data is not None:
            if not self.data.domain.has_continuous_attributes(True, True):
                self.Warning.no_continuous_vars()
                self.data = None

        if self.data is not None and (len(self.data) == 0 or
                                      len(self.data.domain) == 0):
            self.data = None

    def init_attr_values(self):
        # super().init_attr_values()
        data = self.data
        domain = data.domain if data and len(data) else None        
        self.xy_model.set_domain(domain)
        self.attr_x = self.xy_model[0] if self.xy_model else None
        self.attr_y = self.xy_model[1] if len(self.xy_model) >= 2 else self.attr_x
        
        self.attr_changed()
            
    def set_attr(self, attr_x, attr_y):
        if attr_x != self.attr_x or attr_y != self.attr_y:
            self.attr_x, self.attr_y = attr_x, attr_y
            self.attr_changed()

    def set_attr_from_combo(self):
        self.attr_changed()
        # self.xy_changed_manually.emit(self.attr_x, self.attr_y)

    def attr_changed(self):
        self.selected = self.data[:, self.attr_y]
        
        self.setup_plot()
        self.commit()

    def setup_plot(self):    
        if self.subplot is not None:
            self.subplot.clear()
            self.subplot.set_xlabel(self.attr_x.name)
        
        if self.selected is not None:
            self.subplot.plot(self.selected.X, label=self.attr_y.name)
            self.subplot.set_ylabel(self.attr_y.name)
            
        self.commit()
        
        # self.graph.reset_graph()
        # self.__pending_selection = self.selection or self.__pending_selection
        # self.apply_selection()

    def commit(self):
        self.graph.draw()
        
        self.Outputs.selected.send(self.selected)
        
        # super().commit()

    # def handleNewSignals(self):
    #     """Reimplemeted from OWWidget."""
    #     if self.a is not None and self.b is not None:
    #         self.Outputs.sum.send(self.a + self.b)
    #     else:
    #         # Clear the channel by sending `None`
    #         self.Outputs.sum.send(None)

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    # table = Table("iris")
    table = Table("WK1_20200201.csv")
    
    # WidgetPreview(MyWidget).run(set_data=table)
    # WidgetPreview(MyWidget).run()
    
    a = QApplication([])
    ow = MyWidget()

    ow.set_data(table)
    ow.show()
    a.exec()