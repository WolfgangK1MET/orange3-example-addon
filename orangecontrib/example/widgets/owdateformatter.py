import Orange
import Orange.data
from datetime import datetime

from Orange.data import Table, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.widgets import widget, gui

from enum import Enum

class DatetimeType(Enum):
    TOO_MANY_COLUMNS_FOUND = 0
    NO_COLUMN_FOUND = 1
    ISODATETIME = 2
    DE_DATETIME_SEPARATE = 3
    NOT_ENOUGH_COLUMNS_FOUND = 4
    
    

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
        self.Warning.empty_data(shown = self.dataset is None)

    class Inputs:
        data_input = Input("Data", Orange.data.Table)
        
    class Outputs:
        data_output = Output("Data", Orange.data.Table)    
    
    class Error(OWWidget.Error):
        unsupported_date_format = Msg("The given date format is not supported.")
        no_fitting_columns_found = Msg("No date and time column was found.")
    
    class Warning(OWWidget.Warning):
        empty_data = Msg("There is no data to format.")
    
    @Inputs.data_input
    def set_data_input(self, dataset):
        self.Warning.empty_data(shown = dataset is None)
        if dataset is not None:
            self.dataset = dataset
            self.set_output()
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
    def detect_datetime_columns(dataset, date_col_name, time_col_name, datetime_col_name):
        domain = dataset.domain
        domain_attributes = list(domain.attributes)
        domain_metas = list(domain.metas)
        
        count_in_domain = len(list(filter(lambda x: str(x) == date_col_name or str(x) == time_col_name, domain_attributes)))
        count_in_meta = len(list(filter(lambda x: str(x) == date_col_name or str(x) == time_col_name, domain_metas)))
        count = count_in_domain + count_in_meta
        
        if count == 0:
            count = len(list(filter(lambda x: str(x) == datetime_col_name, domain_attributes)))
            count = count + len(list(filter(lambda x: str(x) == datetime_col_name, domain_metas)))
            
            if count == 1:
                return DatetimeType.ISODATETIME
            elif count > 1:
                return DatetimeType.TOO_MANY_COLUMNS_FOUND
            
            return DatetimeType.NO_COLUMN_FOUND
        
        if count == 1:
            return DatetimeType.NOT_ENOUGH_COLUMNS_FOUND
        
        if count == 2:
            return DatetimeType.DE_DATETIME_SEPARATE 
        
        return DatetimeType.TOO_MANY_COLUMNS_FOUND
        
        

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
        
    def set_output(self):
        detectedFormat = DatetimeFormatter.detect_datetime_columns(self.dataset, "Datum", "Uhrzeit", "ISOZEIT")
        self.Error.no_fitting_columns_found(shown = False)
        
        if detectedFormat == DatetimeType.DE_DATETIME_SEPARATE:
            self.checkBoxIncMilliseconds.setDisabled(False)
            self.handle_splitted_date_and_time("Datum", "Uhrzeit", "DatumUhrzeit", "%d.%m.%Y %H:%M:%S,%f")
        elif detectedFormat == DatetimeType.ISODATETIME:
            self.checkBoxIncMilliseconds.setDisabled(True)
            self.handle_date_and_time("ISOZEIT", "DatumUhrzeit",  "%d.%m.%Y %H:%M:%S")
        else:
            self.dataset = None
            self.Error.no_fitting_columns_found(shown = True)
    
    # This function is used for callback, when include_milliseconds is changed
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