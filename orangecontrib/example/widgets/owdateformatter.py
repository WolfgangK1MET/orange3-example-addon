import Orange
import Orange.data
from datetime import datetime

from Orange.data import Table, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import widget, gui

class DatetimeFormatter(OWWidget):
    name = "DatetimeFormatter"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()
        
        self.dataset = None
        self.include_milliseconds = False
        
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        self.checkBoxIncMilliseconds = gui.checkBox(self.optionsBox, self, "include_milliseconds", "Include Milliseconds", callback=self.reloadData)
        self.checkBoxIncMilliseconds.setDisabled(True)

    class Inputs:
        data_input = Input("Data", Orange.data.Table)
        
    class Outputs:
        data_output = Output("Data", Orange.data.Table)    
    
    
    @Inputs.data_input
    def set_data_input(self, dataset):
        if dataset is not None:
            self.dataset = dataset
            self.set_output(self.dataset)
        else:
            self.checkBoxIncMilliseconds.setDisabled(True)
            self.Outputs.data_output.send(None)
    
    @staticmethod
    def is_meta(dataset, attribute_names):
        domain = dataset.domain
        domain_metas = list(domain.metas)
        
        for attribute_name in attribute_names:
            for meta in domain_metas:
                if str(meta) == attribute_name:
                    return True
            
        return False

    @staticmethod
    def is_date_and_time_splitted(dataset):
        domain = dataset.domain
        domain_attributes = list(domain.attributes)
        domain_metas = list(domain.metas)
        
        count_in_domain = len(list(filter(lambda x: str(x) == "Datum" or str(x) == "Uhrzeit", domain_attributes)))
        count_in_meta = len(list(filter(lambda x: str(x) == "Datum" or str(x) == "Uhrzeit", domain_metas)))
        
        return count_in_domain + count_in_meta == 2

    def output_new_table(self, domain_attributes, domain_metas, result_col_name, time_strings, is_datetime_meta):
        if is_datetime_meta == True:
            domain_metas.insert(0, TimeVariable(result_col_name))
        else:
            domain_attributes.insert(0, TimeVariable(result_col_name))
        
        new_domain = Domain(attributes = tuple(domain_attributes), metas = domain_metas, class_vars = self.dataset.domain.class_vars)
        new_table = self.dataset.transform(new_domain)
        
        for index, row in enumerate(new_table): 
            row[result_col_name] = time_strings[index] 
        
        self.Outputs.data_output.send(new_table)

    def handle_splitted_date_and_time(self, date_col_name, time_col_name, result_col_name, formating):
        domain_attributes = list(self.dataset.domain.attributes)
        domain_metas = list(self.dataset.domain.metas)
        time_strings = []
        
        for row in self.dataset:
            dt = datetime.strptime(f'{row[date_col_name]}' + " " + f'{row[time_col_name]}', formating)
            
            if(self.include_milliseconds == False):
                dt = dt.replace(microsecond = 0)
            
            time_strings.append(dt.isoformat(timespec="milliseconds"))
            
        domain_attributes = list(filter(lambda x: str(x) != date_col_name and str(x) != time_col_name, domain_attributes))
        domain_metas = list(filter(lambda x: str(x) != date_col_name and str(x) != time_col_name, domain_metas))
        
        is_datetime_meta =  DatetimeFormatter.is_meta(self.dataset, [date_col_name, time_col_name])
        self.output_new_table(domain_attributes, domain_metas, result_col_name, time_strings, is_datetime_meta)
    
            
    def handle_date_and_time(self, date_and_time_col_name, result_col_name, formating):
        domain_attributes = list(self.dataset.domain.attributes)
        domain_metas = list(self.dataset.domain.metas)
        time_strings = []
        
        for row in self.dataset:
            dt = datetime.strptime(f'{row[date_and_time_col_name]}', formating)
            time_strings.append(dt.isoformat())
            
        domain_attributes = list(filter(lambda x: str(x) != date_and_time_col_name, domain_attributes))
        domain_metas = list(filter(lambda x: str(x) != date_and_time_col_name, domain_metas))
        
        is_datetime_meta =  DatetimeFormatter.is_meta(self.dataset, [date_and_time_col_name])
        self.output_new_table(domain_attributes, domain_metas, result_col_name, time_strings, is_datetime_meta)
        
    def set_output(self, dataset):
        if DatetimeFormatter.is_date_and_time_splitted(dataset):
            self.checkBoxIncMilliseconds.setDisabled(False)
            self.handle_splitted_date_and_time("Datum", "Uhrzeit", "DatumUhrzeit", "%d.%m.%Y %H:%M:%S,%f")
        else:
            self.checkBoxIncMilliseconds.setDisabled(True)
            self.handle_date_and_time("ISOZEIT", "DatumUhrzeit",  "%d.%m.%Y %H:%M:%S")
            
    def reloadData(self):
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