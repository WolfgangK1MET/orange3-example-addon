from enum import IntEnum
from datetime import datetime

import Orange
import Orange.data

from Orange.data import Table, TimeVariable, Domain
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.widgets import gui

WIDGET_NAME = "DatetimeFormatter"
WIDGET_ICON = "icons/mywidget.svg"

class DatetimeFormat(IntEnum):
    UNSUPPORTED = 1
    ISO_DATETIME = 2
    DE_DATETIME_SEPARATE = 3
    
class DatetimeFormatter(OWWidget):
    name = WIDGET_NAME
    icon = WIDGET_ICON 
    want_main_area = False 
    
    class Inputs:
        input_data = Input("Data", Orange.data.Table)
        
    class Outputs:
        output_data = Output("Data", Orange.data.Table)
        
    class Error(OWWidget.Error):
        unsupported_date_format = Msg("The given date format is not supported.")
        no_fitting_columns_found = Msg("No date and time or datetime column was found.")
        
    class Warning(OWWidget.Warning):
        empty_data = Msg("There is no data to format.")
    
    def __init__(self):
        super().__init__()
        
        self.input_dataset = None 
        self.include_milliseconds = False 
        
        self.options_box = gui.widgetBox(self.controlArea, "Options")
        self.cb_include_milliseconds = gui.checkBox(self.options_box, self, "include_milliseconds", "Include Milliseconds", callback = self.reload_data)
        self.cb_include_milliseconds.setDisabled(True)
        
        self.Warning.empty_data(shown = True)
        
    @Inputs.input_data 
    def set_input_data(self, dataset):
        self.input_dataset = dataset 
        
        # Turn of all errors and warnings when new input is set 
        self.Error.no_fitting_columns_found(shown = False)
        self.Error.unsupported_date_format(shown = False)
        self.Warning.empty_data(shown = dataset is None)
        
        # Disable milliseconds checkbox because it is not sure if it is useable
        self.cb_include_milliseconds.setDisabled(True)
        
        if dataset is not None:
            # set_output_data returns true when no error occured
            if self.set_output_data() == True:
                return
        
        # Dataset was none or set_output_data threw an error
        self.input_dataset = None
        self.Outputs.output_data.send(self.input_dataset)
            
    # Returns a boolean that indicates whether the function ran without errors 
    def set_output_data(self):
        detected_format = TableUtility.detect_time_format(self.input_dataset, "ISOZEIT", "Datum", "Uhrzeit")
        is_meta = TableUtility.is_any_attribute_meta(self.input_dataset, "ISOZEIT", "Datum", "Uhrzeit")
        domain_metas = domain_attributes = None
        time_strings = []
        handled = False
        
        if detected_format == DatetimeFormat.ISO_DATETIME:
            self.cb_include_milliseconds.setDisabled(True)
            try:
                time_strings = TableUtility.get_datetime_strings_from_single_column(self.input_dataset, "ISOZEIT", "%d.%m.%Y %H:%M:%S")
            except:
                self.Error.unsupported_date_format(shown = True)
                return handled
            
            domain_attributes, domain_metas = TableUtility.domain_extract_columns(self.input_dataset.domain, "ISOZEIT")
            
        elif detected_format == DatetimeFormat.DE_DATETIME_SEPARATE:
            try:
                time_strings = TableUtility.get_datetime_strings_from_columns(self.input_dataset, "Datum", "Uhrzeit", "%d.%m.%Y %H:%M:%S,%f", self.include_milliseconds)
            except:
                 self.Error.unsupported_date_format(shown = True)
                 return handled
             
            self.cb_include_milliseconds.setDisabled(False)
            domain_attributes, domain_metas = TableUtility.domain_extract_columns(self.input_dataset.domain, "Uhrzeit", "Datum")
            
        else:
            self.Error.no_fitting_columns_found(shown = True)
            return handled
        
        TableUtility.insert_time_col_into_domain(domain_metas, domain_attributes, "DatumUhrzeit", is_meta)
        new_table = TableUtility.generate_new_table(self.input_dataset, domain_attributes, domain_metas)
            
        for index, row in enumerate(new_table):
            row["DatumUhrzeit"] = time_strings[index]
        
        self.Outputs.output_data.send(new_table)
        handled = True
        
        return handled
        
    # Callback function for the checkbox cb_include_milliseconds
    def reload_data(self):
        self.set_input_data(self.input_dataset)
        
        
class TableUtility:
    # The function reads every date and time value in the given columns and concat them. Then it is formatted to a string in iso8601 format.
    # Returns a list of datetime strings in iso8601 format
    @staticmethod
    def get_datetime_strings_from_columns(dataset, date_col_name, time_col_name, formating, include_milliseconds):
        strings = []
        
        for row in dataset:
            strings.append(TableUtility.datetime_string_to_iso8601(f'{row[date_col_name]}' + " " + f'{row[time_col_name]}', formating, include_milliseconds))
            
        return strings
    
    # The function reads every datetime value in the given column and formats it to a string in iso8601 format 
    # Returns a list of datetime strings in iso8601 format
    @staticmethod
    def get_datetime_strings_from_single_column(dataset, datetime_col_name, formating):
        strings = []
        
        for row in dataset:
            strings.append(TableUtility.datetime_string_to_iso8601(f'{row[datetime_col_name]}', formating, False))

        return strings
    
    # The function checks if any given attribute is in the metas of the given dataset domain
    @staticmethod
    def is_any_attribute_meta(dataset, attribute_name, *attribute_names):        
        attribute_names = list(attribute_names)
        attribute_names.append(attribute_name)
        
        for name in attribute_names:
            for meta in dataset.domain.metas:
                if str(meta) == name:
                    return True
        
        return False
    
    @staticmethod
    def datetime_string_to_iso8601(time_string, formating, include_milliseconds):
        dt = datetime.strptime(time_string, formating)

        if(include_milliseconds == False):
            dt = dt.replace(microsecond = 0)
        
        return dt.isoformat(timespec="milliseconds")
    
    # Checks if all given column names are in the domain of the given dataset
    @staticmethod
    def are_all_column_names_in_table(dataset, column_name, *column_names):
         column_names = list(column_names)
         column_names.append(column_name)
         domain_attributes = list(dataset.domain.attributes) + list(dataset.domain.metas)

         for name in column_names:
             is_in_table = False
             
             for attribute in domain_attributes:
                 if str(attribute) == str(name):
                     is_in_table = True
                     
             if is_in_table == False:
                return False 
        
         return True
    
    # Detects whether it is DatetimeFormat.ISO_DATETIME or DatetimeFormat.DE_DATETIME_SEPARATE format.
    # Returns the detected format if the format is known otherwise it returns DatetimeFormat.UNSUPPORTED
    @staticmethod
    def detect_time_format(dataset, column_name, *column_names):        
        if TableUtility.are_all_column_names_in_table(dataset, column_name):
            return DatetimeFormat.ISO_DATETIME  
        
        if TableUtility.are_all_column_names_in_table(dataset, *column_names):
            return DatetimeFormat.DE_DATETIME_SEPARATE 
        
        return DatetimeFormat.UNSUPPORTED 
    
    # Inserts a new TimeVariable with the given column name into the domain
    @staticmethod 
    def insert_time_col_into_domain(domain_metas, domain_attributes, col_name, is_meta):
        if is_meta == True:
            domain_metas.insert(0, TimeVariable(col_name))
        else:
            domain_attributes.insert(0, TimeVariable(col_name))
    
    # Returns the domain without the given column names
    @staticmethod 
    def domain_extract_columns(domain, column_name, *column_names):
        columns = list(column_names)
        columns.append(column_name)
        
        attributes = domain.attributes
        metas = domain.metas
        
        for name in columns:
            attributes = list(filter(lambda x: str(x) != name, attributes))
            
        for name in columns:
            metas = list(filter(lambda x: str(x) != name, metas))
            
        return (attributes, metas)
            
    @staticmethod 
    def generate_new_table(dataset, domain_attributes, domain_metas):
        new_domain  = Domain(attributes = tuple(domain_attributes), metas = domain_metas, class_vars = dataset.domain.class_vars)
        new_table = dataset.transform(new_domain)
        
        return new_table
    
    
if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    
    table = Table("HOA_ADMIN_HOA_DRUCK.csv")
    
    a = QApplication([])
    df = DatetimeFormatter()

    df.set_input_data(table)
    
    df.show()
    a.exec()
            