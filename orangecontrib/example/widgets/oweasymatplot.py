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

# Todo 
# Weitere Achsen können mit dem Dictionary des Objekts hinzugefügt werden. 
# self.__dict__[attribute_name] = value 
# self.__dict__[attribute_name] = None // entfernen 



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
        
        self.attr_x = None
        self.attr_y = None
        
        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        
        self.cb_attr_x = gui.comboBox(self.attr_box, self, "attr_x", label="Axis x:", callback=self.set_attr_x_from_combo, model=self.x_model, **common_options, searchable = True)
        self.axis_box = gui.vBox(self.attr_box, True)
        self.cb_attr_y = gui.comboBox(self.axis_box, self, "attr_y", label="Axis y:", callback=self.set_attr_y_from_combo, model=self.y_model, **common_options, searchable = True)
        
        self.axis_h_box = gui.hBox(self.axis_box, True)
        self.b_attr_remove = gui.button(self.axis_h_box, self, label="Remove", callback=self.set_attr_y_from_combo)
        self.b_attr_edit = gui.button(self.axis_h_box, self, label="Edit", callback=self.set_attr_y_from_combo)
        
        self.cb_attr_y = gui.comboBox(self.axis_box, self, "attr_y", label="Axis y:", callback=self.set_attr_y_from_combo, model=self.y_model, **common_options, searchable = True)
        
        self.axis_h_box = gui.hBox(self.axis_box, True)
        self.b_attr_remove = gui.button(self.axis_h_box, self, label="Remove", callback=self.set_attr_y_from_combo)
        self.b_attr_edit = gui.button(self.axis_h_box, self, label="Edit", callback=self.set_attr_y_from_combo)
        
        self.b_attr_edit = gui.button(self.axis_box, self, label="Add y", callback=self.set_attr_y_from_combo)
        
        self.graph = MatplotlibWidget()
        gui.rubber(self.attr_box)
        self.new_plot = gui.button(self.controlArea, self, label="Add plot", callback=self.set_attr_y_from_combo)
        
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
            self.__update_plot()
            
        self.Outputs.selected.send(self.__input_data)
    
    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)
        
        return time_var
    
    def __update_plot(self):
        self.selected = self.__input_data[:, self.attr_y] # Wie, wenn mehrere attr_y?
        self.subplot.clear()

        x = []
        y = self.selected
        
        for row in self.__input_data:
            x.append(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
        
        myFmt = mdates.DateFormatter('%H:%M:%S')
        self.subplot.xaxis.set_major_formatter(myFmt)
        self.subplot.plot(x, y)
        self.__commit()


    def __commit(self):
        pass
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