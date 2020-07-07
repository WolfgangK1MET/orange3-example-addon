import Orange
import Orange.data
from datetime import datetime

from Orange.data import Table, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

class DatetimeFormatter(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "DatetimeFormatter"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        self.checkBox = gui.checkBox(self.optionsBox, self, "include_milliseconds", "Include Milliseconds", callback=self.incMilli)
            
        self.dataset = None
        self.checkBox.setDisabled(True)
        self.include_milliseconds = False
        
    class Inputs:
        data_input = Input("Data", Orange.data.Table)

    class Outputs:
        data_output = Output("Data", Orange.data.Table)    
    
    @Inputs.data_input
    def set_data_input(self, dataset):
        if dataset is not None:
            self.dataset = dataset
            self.set_output(self.data_input)
        else:
            self.checkBox.setDisabled(True)
            self.Outputs.data_output.send(None)
    
    @staticmethod
    def is_date_and_time_splitted(dataset):
        return True  

    def handle_splitted_date_and_time(self, dataset, date_col_name, time_col_name, result_col_name, formating):
        time_strings = []


    def handle_date_and_time(self, dataset, date_and_time_col_name, result_col_name, formating):
        pass

    def set_output(self, dataset):
        
        
        if is_date_and_time_splitted(dataset):
            self.handle_splitted_date_and_time(dataset)
        else:
            self.handle_date_and_time(dataset)
        
        
        
        domain = dataset.domain
        domain_attributes = list(domain.attributes)
        domain_metas = list(domain.metas)
        is_date_or_time_meta = False
        
        for row in dataset:
            dt = datetime.strptime(f'{row["Datum"]}' + "  " + f'{row["Uhrzeit"]}', format_str)

            if(self.include_milliseconds == False):
                dt = dt.replace(microsecond = 0)
            
            time_strings.append(dt.isoformat(timespec="milliseconds"))

        date_count = len(list(filter(lambda x: str(x) == "Datum" or str(x) == "Uhrzeit", domain_attributes)))
        
        if date_count < 2:
            is_date_or_time_meta = True
        
        
        if is_date_or_time_meta == True:
            domain_metas.append(TimeVariable("DatumUhrzeit"))
        else:
            domain_attributes.append(TimeVariable("DatumUhrzeit"))
        
        domain_attributes = list(filter(lambda x: str(x) != "Datum" and str(x) != "Uhrzeit", domain_attributes))
        domain_metas = filter(lambda x: str(x) != "Uhrzeit" and str(x) != "Datum", domain_metas)

        new_domain = Domain(attributes = tuple(domain_attributes), metas = domain_metas, class_vars = domain.class_vars)
        new_table = dataset.transform(new_domain)
        
        for index, row in enumerate(new_table): 
            row["DatumUhrzeit"] = time_strings[index] 
        
        self.checkBox.setDisabled(False)
        
        self.Outputs.data_output.send(new_table)
        
        
    def incMilli(self):
        self.set_data_input(self.dataset)

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    # table = Table("iris")
    table = Table("WK1_20200201_orig.csv")

    
    a = QApplication([])
    df = DatetimeFormatter()

    df.set_data_input(table)
    
    df.show()
    a.exec()