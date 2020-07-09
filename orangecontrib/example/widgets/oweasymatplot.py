import Orange

from Orange.data import Table
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import TimeVariable, Domain
from Orange.widgets import gui

from AnyQt.QtCore import Qt


class OWEasyMatplot(OWWidget):
    name = "Easymatplot-test"
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
        
        self.__input_data = None
        self.Warning.empty_data(shown = True)
        
        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, sendSelectedValue=True, contentsLength=14)
        
        self.attr_box = gui.vBox(self.controlArea, True)
        self.x_axes = []
        

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset
        self.Warning.empty_data(shown = True)
        
        if dataset is not None:
            self.Warning.empty_data(shown = False)
            self.__detect_time_variable()
        else:
            self.Output.selected.send(self.__input_data)
    
    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)
        
        
        
class TableUtility:
    @staticmethod
    def get_first_time_variable(dataset):
        for attribute in list(dataset.domain.metas) + list(dataset.domain.attributes):
            if type(attribute) == TimeVariable:
                return attribute
            
        return None
        

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("WK1_20200201.csv")
    
    a = QApplication([])
    df = OWEasyMatplot()

    df.set_data(table)
    
    df.show()
    a.exec()