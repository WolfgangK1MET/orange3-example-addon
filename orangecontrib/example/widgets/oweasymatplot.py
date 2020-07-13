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



# Todo 
# Weitere Achsen können mit dem Dictionary des Objekts hinzugefügt werden. 
# self.__dict__[attribute_name] = value 
# self.__dict__[attribute_name] = None // entfernen 

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %('double' if event.dblclick else 'single', event.button, event.x, event.y, event.xdata, event.ydata))

# To create a second window, maybe there is another way
class Second(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)

class OWEasyMatplot(OWWidget):
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
        
        self.__input_data = None
        self.Warning.empty_data(shown = True)
        
        common_options = dict(labelWidth=50, orientation=Qt.Horizontal, sendSelectedValue=True, contentsLength=14)
        

        self.attr_box = gui.vBox(self.controlArea, True)
        
        self.attr_x = None
        self.attr_y1 = None
        self.attr_y2 = None
        
        # How to create second window 
        # self.second_window = Second(self)
        # self.second_window.show()
        
        dmod = DomainModel
        self.x_model = DomainModel(dmod.MIXED, valid_types=TimeVariable)
        self.y_model = DomainModel(dmod.MIXED, valid_types=ContinuousVariable)
        self.attr_y0 = None
        self.attr_y1 = None
        
        # attr_x wird leider immer benötigt, da comboBox ansonsten das Argument 'value' vermisst.
        self.cb_attr_x = gui.comboBox(self.attr_box, self, "attr_x", label="Axis x:", callback=self.set_attr_x_from_combo, model=self.x_model, **common_options, searchable = True)
        self.axis_box = gui.vBox(self.attr_box, True)
        
        self.cb_attr_y0 = gui.comboBox(self.axis_box, self, "attr_y0", label="Axis y:", callback=self.set_attr_y_from_combo, model=self.y_model, **common_options, searchable = True)
        self.axis_h_box0 = gui.hBox(self.axis_box, True)
        self.b_attr_remove0 = gui.button(self.axis_h_box0, self, label="Remove", callback=self.set_attr_y_from_combo)
        self.b_attr_edit0 = gui.button(self.axis_h_box0, self, label="Edit", callback=self.set_attr_y_from_combo)
        
        self.cb_attr_y1 = gui.comboBox(self.axis_box, self, "attr_y1", label="Axis y:", callback=self.set_attr_y_from_combo, model=self.y_model, **common_options, searchable = True)
        self.axis_h_box1 = gui.hBox(self.axis_box, True)
        self.b_attr_remove1 = gui.button(self.axis_h_box1, self, label="Remove", callback=self.set_attr_y_from_combo)
        self.b_attr_edit1 = gui.button(self.axis_h_box1, self, label="Edit", callback=self.set_attr_y_from_combo)
        
        self.graph = MatplotlibWidget()
        gui.rubber(self.attr_box)
        
        box = gui.vBox(self.mainArea, True, margin=0)
        box.layout().addWidget(self.graph)
        self.subplot = self.graph.getFigure().add_subplot()
        self.ax1 = self.subplot.twinx()
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
            
            # TODO: Throw exception if there is no datetime or/and number type
            self.attr_x = time_var 
            self.attr_y0 = self.y_model[1] # TODO: check if there is one ... // method needed which get first number type ...
            self.attr_y1 = self.y_model[2] # TODO: check if there is one ... // method needed which get first number type ...
            
            self.cid = self.graph.canvas.mpl_connect('draw_event', onclick)
            
            self.__update_plot()
            
        self.Outputs.selected.send(self.__input_data)
    
    def __detect_time_variable(self):
        time_var = TableUtility.get_first_time_variable(self.__input_data)
        
        return time_var
    
    def __update_plot(self):
        self.subplot.clear()
        self.ax1.clear()
        
        x = []
        for row in self.__input_data:
            x.append(dateutil.parser.parse(f'{row["DatumUhrzeit"]}'))
        y = self.selected = self.__input_data[:, self.attr_y0] # Wie, wenn mehrere attr_y?

        self.subplot.set_xlabel(self.attr_x.name)
        self.subplot.set_ylabel(self.attr_y0.name, color = "r")
        self.ax1.set_ylabel(self.attr_y1.name, color = "b")

        # Keine Tage werden berücksichtigt, hierfür wäre eine Einstellung sinnvoll
        myFmt = mdates.DateFormatter('%H:%M:%S')
        self.subplot.xaxis.set_major_formatter(myFmt)
        self.ax1.xaxis.set_major_formatter(myFmt)
        
        plot0 = self.subplot.plot(x, y, label = self.attr_y0.name, color = "r")
        plot1 = self.ax1.plot(x, self.__input_data[:, self.attr_y1], label = self.attr_y1.name, color = "b")

        self.plots = plot0 + plot1
        self.labels = [self.attr_y0.name, self.attr_y1.name]

        self.graph.getFigure().tight_layout()
        self.__commit()

    def __commit(self):
        self.subplot.legend(self.plots, self.labels, loc = 0)

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