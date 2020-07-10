
class Row:
    def __init__(self, length):
        self.elements = [None] * length * 2
        
    def __getitem__(self, key):
        return self.elements[key]
    
    def __setitem__(self, key, value):
        self.elements[key] = value
        
class EditableTable:
    def __init__(self, row_count, column_count):
        self.elements = [None] * row_count * 2
        
        for i in range(0, row_count):
            self.elements[i] = Row(column_count * 2)
    
    def __getitem__(self, key):
        return self.elements[key]
    
class SomeObject:
    def __init__(self):
        pass

table = EditableTable(10, 20)
