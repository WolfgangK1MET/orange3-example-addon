import Orange

from Orange.data import Table, ContinuousVariable
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import TimeVariable, Domain
from Orange.widgets import gui
from Orange.widgets.utils.itemmodels import DomainModel
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import dateutil.parser
import matplotlib
import datetime
import random

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
        
        # self.__dict__[...]
        
        self.attr_box = gui.vBox(self.controlArea, True)
        self.attr_x = None
        self.attr_y = None
        
        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        
        self.axis_box = gui.vBox(self.attr_box, True)
        self.cb_attr_x = gui.comboBox(self.axis_box, self, "attr_x", label="Axis x:", callback=self.set_attr_x_from_combo, model=self.x_model, **common_options, searchable = True)
        self.cb_attr_y = gui.comboBox(self.axis_box, self, "attr_y", label="Axis y:", callback=self.set_attr_y_from_combo, model=self.y_model, **common_options, searchable = True)
        
        self.graph = MatplotlibWidget()
        
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        self.subplot = self.graph.getFigure().add_subplot()
        
        self.show()
        
    # Callback function for cb_attr_x
    def set_attr_x_from_combo(self):
        self.__update_plot()
    
    # Callback function for cb_attr_y
    def set_attr_y_from_combo(self):
        self.__update_plot()

    @Inputs.data
    def set_data(self, dataset):
        self.__input_data = dataset
        self.Warning.empty_data(shown = True)
        
        if dataset is not None:
            self.Warning.empty_data(shown = False)
            time_var = self.__detect_time_variable()
            
            self.x_model.set_domain(dataset.domain)
            self.y_model.set_domain(dataset.domain)
            self.attr_x = time_var 
            self.attr_y = self.y_model[1] # check if there is one ... // method needed which get first number type ...
            
        self.Outputs.selected.send(self.__input_data)
    
    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)
        
        return time_var
    
    def __update_plot(self):
        self.selected = self.__input_data[:, self.attr_y] # Wie, wenn mehrere attr_y?
        
        self.__setup_plot()
        self.__commit()
        
    def __setup_plot(self):
        if self.subplot is not None:
            self.subplot.clear()
            yLabel = ""
            
            if self.selected is not None:
                print(self.selected)
                self.subplot.plot(self.selected, label=self.attr_y.name)
                ylabel = self.attr_y.name;
                
            x_names = []
            
            for row in self.__input_data:
                x_names.append(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
                print(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
                
            for i in self.selected:
                print(i)
            
            x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(12)]
            y = [i+random.gauss(0,1) for i,_ in enumerate(x)]
            
            self.subplot.set_xtick()
  
    def __commit(self):
        self.subplot.legend()
        self.graph.draw()
        
        self.Outputs.selected.send(self.selected)
        
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