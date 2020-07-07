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
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt

# class MyWidget(OWDataProjectionWidget):
class OWEasyPlot(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Easy Matplot"
    description = "A widget for easy plots with matplotlib"
    icon = "icons/oweasyplot.svg"
    want_main_area = True
    
    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        selected = Output("Selected Data", Orange.data.Table)

    attr_list = [ContextSetting(None)]
    attr_x = ContextSetting(None)
    attr_y = ContextSetting(None)
    attr_y1 = ContextSetting(None)
    attr_y2 = ContextSetting(None)
    attr_y3 = ContextSetting(None)
    attr_y4 = ContextSetting(None)
    attr_y5 = ContextSetting(None)
    
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
        # self.btnAdd.setEnabled(False)

        dmod = DomainModel
        self.xy_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        
        self.axis_box = gui.vBox(self.attr_box, True)
        self.cb_attr_x = gui.comboBox(
            self.axis_box, self, "attr_x", label="Axis x:",
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        # self.cb_attr_x.setEnabled(False)
        
        self.cb_attr_y = gui.comboBox(
            self.axis_box, self, "attr_y", label="Axis y0:",
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        
        # self.configsArea.layout().addWidget(config)
        
        self.btn_list = [self.cb_attr_y]        
        
        gui.rubber(self.attr_box);
        
        self.calcBox = gui.vBox(self.attr_box, True)
        self.deOffsetBtn = gui.button(self.calcBox, self, "Remove Offset", 
                                 callback=self.deOffset)   
        self.deOffsetBtn.setEnabled(False)
        self.xCorrBtn = gui.button(self.calcBox, self, "X-Correlate", 
                                 callback=self.xCorr)   
        self.xCorrBtn.setEnabled(False)
        self.corrData = None
        
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
        # self.subplot2 = self.graph.getFigure().add_subplot()
        
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

    def addAxis(self):
        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, 
                              sendSelectedValue=True, contentsLength=14)
        cb_attr_y = gui.comboBox(
            self.axis_box, self, "attr_y%i" %len(self.btn_list), label="Axis y%i:" %len(self.btn_list),
            callback=self.set_attr_from_combo,
            model=self.xy_model, **common_options,
            searchable=True)
        # cb_attr_y.setEnabled(False)
        
        self.btn_list.append(cb_attr_y)
        self.attr_list.append(ContextSetting(None))
                
        self.btnAdd.setDisabled(len(self.btn_list) >= 5)
        # self.deOffsetBtn.setEnabled(True)
        self.xCorrBtn.setEnabled(True)

    def deOffset(self):
        self.data[:, self.attr_y].X = self.data[:, self.attr_y].X-np.mean(self.data[:, self.attr_y].X)
        self.data[:, self.attr_y1].X = self.data[:, self.attr_y1].X-np.mean(self.data[:, self.attr_y1].X)
        
        self.commit()

    def xCorr(self):
        x1 = np.array(self.data[:, self.attr_y].X)
        x1 = x1-np.mean(x1)
        x1 = np.reshape(x1, len(x1))
        x2 = np.array(self.data[:, self.attr_y1].X)
        x2 = x2-np.mean(x2)
        x2 = np.reshape(x2, len(x2))
        
        self.corrData = np.correlate(x1, x2, "Same")        
        # corrData = corrData/np.max(corrData)
        
        maxTop = np.max([self.data[:, self.attr_y].X, self.data[:, self.attr_y1].X])
        minBot= np.min([self.data[:, self.attr_y].X, self.data[:, self.attr_y1].X])
        self.corrData = (self.corrData/np.max(self.corrData) + 1)/2        
        self.corrData = self.corrData*(maxTop-minBot) + minBot;
        
        self.attr_changed()

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

    # def set_attr_list_from_combo(self):

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
            yLabel = ''
            
            if self.selected is not None:
                self.subplot.plot(self.selected.X, label=self.attr_y.name)
                ylabel = self.attr_y.name;
                
            if len(self.attr_list) > 1:
                self.subplot_axis(self.attr_y1)
                ylabel = ylabel + self.attr_y1.name
                
            if len(self.attr_list) > 2:
                self.subplot_axis(self.attr_y2)
                ylabel = ylabel + self.attr_y2.name
                
            if len(self.attr_list) > 3:
                self.subplot_axis(self.attr_y3)
                
            if len(self.attr_list) > 4:
                self.subplot_axis(self.attr_y4)
                
            if len(self.attr_list) > 5:
                self.subplot_axis(self.attr_y5)
            
            self.subplot.set_xlabel(self.attr_x.name)
            self.subplot.set_ylabel(ylabel)

            # only valid for WK1_20200201.csv for demo purposes
            self.subplot.set_xticks([0, 40, 80, 120, 160])
            x0 = "00:04:56"
            x1 = "05:29:26"
            x2 = "11:00:56"
            x3 = "16:38:16"
            x4 = "22:15:15"
            self.subplot.set_xticklabels([x0, x1, x2, x3, x4])
            
            # self.subplot.set_xticklabels(["$0$", r"$2$", r"$3$", r"$4$", r"$5$"])
            # self.subplot.set_xticklabels(["$0$", r"$\frac{1}{2}\pi$",
                     # r"$\pi$", r"$\frac{3}{2}\pi$", r"$2\pi$"])
            
            if(self.corrData is not None):
                self.subplot.plot(self.corrData, label='X-Corr')
                secax = self.subplot.secondary_yaxis('right', functions=(self.Y1, self.Y2))
                secax.set_ylabel('X-Corr')
                # self.subplot.set_y2label('X-Corr')
            
        self.commit()
        
        # self.graph.reset_graph()
        # self.__pending_selection = self.selection or self.__pending_selection
        # self.apply_selection()
            
    def Y1(self, y):
        return y
    
    
    def Y2(self, y):
        return (y - 3)

    def subplot_axis(self, attr):
        self.subplot.plot(self.data[:, attr].X, label=attr.name)
        # self.subplot.set_ylabel(attr.name)        

    def commit(self):
        self.subplot.legend()
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
    
    a = QApplication([])
    ow = OWEasyPlot()

    ow.set_data(table)
    ow.show()
    a.exec()