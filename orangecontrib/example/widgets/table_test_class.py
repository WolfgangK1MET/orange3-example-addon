import numpy as np

class Column:
    def __init__(self, length, var_type):
        self.elements = np.empty([length * 2], dtype = var_type)
        
    def __getitem__(self, key):
        return self.elements[key]
    
    def __setitem__(self, key, value):
        self.elements[key] = value
        
    def add_element(self, element):
        pass
        # if length ... resize ...
        
    def __resize(self):
        pass
    
class EditableTable:
    def __init__(self, row_count, column_count):
        self.elements = np.empty([row_count * 2], dtype = Column)
        
        self.row_count = row_count
        self.column_count = column_count
        
        for i in range(0, column_count):
            self.elements[i] = Column(column_count * 2, None)
    
    def __getitem__(self, key):
        return self.elements[key]
    
    def change_column_type(self, column_name):
        pass
    
    def add_row(self, *values):
        pass
    
    def add_column(self, column_name, column_type):
        pass
    
    def to_table(self):
        pass
    
    def __resize_columns(self):
        self.elements = np.empty(self.elements, dtype = Column)
        # copy tmp -> resized elements wäre wohl besser
        
    
    def __resize_rows(self):
        # Columns müssen neu erstellt werden, jeder Column muss doppelt so lang gemacht werden.
        pass
        
    # x.astype(float) // oder anderen Typ, den man haben möchte. Typumwandlung numpy ...
    
class SomeObject:
    def __init__(self):
        pass

table = EditableTable(10, 20)
