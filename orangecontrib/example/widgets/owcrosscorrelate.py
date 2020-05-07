# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 09:22:15 2020

@author: U864414
"""

import sys
import Orange
import Orange.data
import numpy as np
# import scipy as sp

# from functools import partial
# from typing import Optional

from Orange.data import ContinuousVariable
from Orange.data.table import Table, Domain

from Orange.widgets import gui, widget, settings
# from Orange.widgets.settings import ContextSetting, Setting, DomainContextHandler
# from Orange.widgets.utils import vartype
# from Orange.widgets.utils.listfilter import VariablesListItemView, slices, variables_filter
# from Orange.widgets.utils.state_summary import format_summary_details
from Orange.widgets.widget import Input, Output, AttributeList
from Orange.widgets.utils.itemmodels import VariableListModel

from orangecontrib.timeseries import Timeseries

def rescale(data):
    seq = np.reshape(data, len(data))
    return (seq-min(seq))/(max(seq)-min(seq))

def getIntegralQuartileIndex(a):
    ss = sum(a)
    s = 0
    q1, q2, q3 = 0,0,0
    for i in range(len(a)):
      s+=a[int(i)]
      if s == 0 and ss == 0:
          continue
      elif (q1 == 0 and s/ss>0.25):
          q1 = int(i)
      elif (q2 == 0 and s/ss>0.5):
          q2 = int(i)
      elif (q3 == 0 and s/ss>0.75):
          q3 = int(i)
        
    return [q1, q2, q3]

class OWCrossCorrelate(widget.OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Cross Correlate"
    description = "A widget for cross correlations"
    icon = "icons/mywidget.svg"
    priority = 10
    
    class Inputs:
        dataHOA  = Input("HOA Data", Table)
        dataKGB  = Input("KGB Data", Table)

    class Outputs:
        dataCorr = Output("Correlated Data", Table)

    want_main_area = False
    resizing_enabled = False
    
    radio_sequential = settings.Setting(0)
    selected_attr = settings.Setting('')
    autocommit = settings.Setting(True)
    
    def __init__(self):
        super().__init__()
        self.dataHOA = None
        self.dataKGB = None
        
        self.dataCorr = None
                
        # GUI        
        box = gui.vBox(self.controlArea, 'Sequence')
        group = gui.radioButtons(box, self, 'radio_sequential',
                                 callback=self.on_changed)
        hbox = gui.hBox(box)
        gui.appendRadioButton(group, 'Correlate only:',
                              insertInto=hbox)

        attrs_model = self.attrs_model = VariableListModel()
        combo_attrs = self.combo_attrs = gui.comboBox(
            hbox, self, 'selected_attr',
            callback=self.on_changed,
            sendSelectedValue=True)
        combo_attrs.setModel(attrs_model)

        gui.appendRadioButton(group, 'Correlate all HOA Data',
                              insertInto=box)

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No data on input HOA yet, waiting to get something.")
        self.infob = gui.widgetLabel(box, "No data on input KGB yet, waiting to get something.")
        
        gui.auto_commit(self.controlArea, self, 'autocommit', '&Apply')

    def on_changed(self):
        self.commit()
        
    def commit(self):
        dataHOA = self.dataHOA
        dataKGB = self.dataKGB
        
        if dataHOA is None:
            self.infoa.setText("No data on data HOA input yet.")
        else:
            self.infoa.setText("%d instances in data set HOA" % len(dataHOA))
                
        if dataKGB is None:
            self.infob.setText("No data on data KGB input yet.")
        else:
            self.infob.setText("%d instances in data set KGB" % len(dataKGB))

        if dataHOA is None or dataKGB is None or (self.selected_attr not in dataHOA.domain and not self.radio_sequential):
            self.Outputs.dataCorr.send(None)
            return

        corrData = np.array([])
        quartiles = np.array([]);
        dq1q3 = np.array([]);
        
        for i, r in enumerate(dataKGB):
            fineHist = np.array(r[-200:])
            q = getIntegralQuartileIndex(fineHist)
            quartiles = np.concatenate(quartiles, q)
            dq1q3 = np.concatenate(dq1q3, abs(q[0]-q[2]))
        
        if self.radio_sequential:
            # calculate correlation only for selected HOA data
            hoa_col = dataHOA[:, self.selected_attr]
            c = rescale(hoa_col)
            corr = np.correlate(c, dq1q3, "full")
            # corr = np.correlate(data1, data2, "full")
        else:                
            # calculate correlation for all HOA data
            for hoa_col in dataHOA:
                c = rescale(hoa_col)
                corr = np.correlate(c, dq1q3, "full")
                
        corrData = np.concatenate(corrData, corr)
        domain = Domain.from_numpy(corrData)
        
        # domain = Domain([ContinuousVariable.make("gender"),
        #                 ContinuousVariable.make("age"), 
        #                 ContinuousVariable.make("salary")])
        
        t = Table.from_numpy(domain, corrData)
        
        self.Outputs.dataCorr.send(corr)
    
    @Inputs.dataHOA
    def set_dataHOA(self, data):
        if data is not None:
            self.dataHOA = data;
            # self.combine_datasets();
            
            # from owtabletotimeseries            
            if data.domain.has_continuous_attributes():
                vars = [var for var in data.domain.variables if var.is_time] + \
                       [var for var in data.domain.metas if var.is_time] + \
                       [var for var in data.domain.variables
                        if var.is_continuous and not var.is_time] + \
                       [var for var in data.domain.metas if var.is_continuous and
                        not var.is_time]
                self.attrs_model.wrap(vars)
                self.selected_attr = data.time_variable.name if getattr(data, 'time_variable', False) else vars[0].name
            
        self.on_changed()
    
    @Inputs.dataKGB
    def set_dataKGB(self, data):
        if data is not None:
            self.dataKGB = data;
            # self.combine_datasets();
            
        self.on_changed()
            
if __name__ == "__main__":
    # from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    # WidgetPreview(OWCrossCorrelate).run()

    datahoa = Table.from_file(r"C:\dev\data\Abfrage_Ofendaten_Druck_Sinterstillstand_2.csv")
    datakgb = Table.from_file(r"C:\dev\data\WK1_20200201.csv")
    
    ow = OWCrossCorrelate()
    ow.set_dataHOA(datahoa)
    ow.set_dataKGB(datakgb)
    ow.show()