import Orange
import Orange.data
import numpy as np
import scipy as sp

from AnyQt.QtWidgets import QLabel
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget,gui

class MyWidget(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Test WG"
    description = "A widget for tests from Wolfgang"
    icon = "icons/mywidget.svg"
    want_main_area = False
    
    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        sample = Output("Sampled Data", Orange.data.Table)

    want_main_area = False

    def __init__(self):
        super().__init__()
        
        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, "No data on input yet, waiting to get something.")
        self.infob = gui.widgetLabel(box, '')
            
        
    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText("%d instances in input data set" % len(dataset))
            indices = np.random.permutation(len(dataset))
            indices = indices[:int(np.ceil(len(dataset) * 0.1))]
            sample = dataset[indices]
            self.infob.setText("%d sampled instances" % len(sample))
            self.Outputs.sample.send(sample)
        else:
            self.infoa.setText(
                "No data on input yet, waiting to get something.")
            self.infob.setText('')
            self.Outputs.sample.send(None)

    # def handleNewSignals(self):
    #     """Reimplemeted from OWWidget."""
    #     if self.a is not None and self.b is not None:
    #         self.Outputs.sum.send(self.a + self.b)
    #     else:
    #         # Clear the channel by sending `None`
    #         self.Outputs.sum.send(None)

if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(MyWidget).run()
