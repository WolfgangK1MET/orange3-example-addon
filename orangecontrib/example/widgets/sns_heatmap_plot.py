import seaborn as sns; sns.set(style="ticks", color_codes=True)
import Orange

from collections import OrderedDict
from Orange.data import Table, Domain, ContinuousVariable, DiscreteVariable

import numpy as np
import pandas as pd
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from matplotlib import pyplot as plt
import seaborn as sns
from Orange.widgets import gui
from Orange.data.pandas_compat import table_from_frame,table_to_frame
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget


class OWSeabornHeatmap(OWWidget):
    name = "seaborn correlation plot"
    description = "Widget Test seaborn"
    icon = "icons/oweasyplot.svg"
    want_main_area = True
    want_control_area = True

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
        self.data=None
        self.graph = MatplotlibWidget()
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        

    @Inputs.data
    def set_input_data(self, dataset):
        if dataset is not None:
            self.data = dataset
            self.dataf = table_to_frame(dataset)
        else:
            self.Outputs.selected.send(None)
            
        self.update()
        self.show()

    def update(self):
        corr = self.dataf.corr()
        fig = self.graph.getFigure()
        fig.clear()
        ax=fig.add_subplot(111)
        sns.heatmap(corr,cmap="coolwarm",square=True,vmax=1,vmin=-1,center=0,linewidth=.5,annot=True,ax=ax)
        self.graph.draw()


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    datafr = pd.DataFrame({'num_legs': [2, 4, 8, 0],
                   'num_wings': [2, 0, 0, 0],
                   'num_specimen_seen': [10, 2, 1, 8]},
                  index=['falcon', 'dog', 'spider', 'fish'])
    table = table_from_frame(datafr)

    a = QApplication([])
    df = OWSeabornHeatmap()

    df.set_input_data(table)
    df.update()
    df.show()
    a.exec()
