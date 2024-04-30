import csv 
import re
from ahe_mb.models import ENCODINGS,FORMATS,Map,Field,BitMap,BitValue

MODBUS_COLUMN = ['name', 'description', 'field_address', 'field_encoding', 'field_format', 'field_scale', 'field_offset', 'field_size', 'bit_map']
MODBUS_NON_BLANK_COLUMN =  ['field_address', 'field_format', 'field_size', 'field_scale', 'field_offset', 'description', 'name']

BIT_MAP_COLUMN = ["ahe_name","start_bit","end_bit","description"]
BIT_MAP_NON_BLANK_COLUMN = ["ahe_name","start_bit","end_bit","description"]

VALID_ENCODING = [e[0] for e in ENCODINGS] 
VALID_FORMAT = [f[0] for f in FORMATS]


def change_csv_format(datas):
    mb_data = []
    for data in datas:
        d = {
            "name":data["ahe_name"],
            "field_address":data["memory_address"],
            "description":data["description"],
            "field_encoding":data["encoding"],
            "field_format":data["format"],
            "field_scale":data["scale"],
            "field_offset":data["offset"],
            "field_size":data["size"],
            "bit_map":data["bit_map"]

        }
        mb_data.append(d)
    return mb_data

def is_valid_literal(text):
    re1 = re.compile(r"^[a-zA-z]\w*$")
    return re1.search(text)

class FileLoader:

    def __init__(self):
        self.columns = None 
        self.non_blank_column = None

    def validate_column(self):
        keys = self.data[0].keys()
        for expected_column in self.columns:
            if expected_column not in keys:
                self.add_error(
                    0, expected_column,
                    f'{expected_column} is required in the header')

    def validate_blank_value(self):
        row = 1
        for d in self.data:
            for key in d:
                if key in self.non_blank_column and d[key] == '':
                    self.add_error(row, key,"value should not be blank")
            row+=1

    def check_valid_literal(self, row, row_data,column):
        if not is_valid_literal(row_data[column]):
            print("error found ", row_data[column])
            self.add_error(row, column,
                           f"invalid name '{row_data[column]}'")
            return False 
        return True
    
    def is_invalid_int(self, row, row_data, column):
        try:
            _ = int(eval(row_data[column]))
        except ValueError as e:
            self.add_error(row, column, f' invalid integer value:{row_data[column]}')
            return True 
        return False

    def is_invalid_float(self, row, row_data, column):
        try:
            _ = float(eval(row_data[column]))
        except ValueError as e:
            self.add_error(row, column, f' invalid float value:{row_data[column]}')
    
    def add_error(self, row, col, error):
        error = f"{error} Row: {row} Column: {col}"
        self.errors.append(error)
    

class ModbusLoader(FileLoader):

    def __init__(self, data,map_name):
        self.columns = MODBUS_COLUMN
        self.data = data
        self.non_blank_column = MODBUS_NON_BLANK_COLUMN
        #self.data = change_csv_format(data)
        self.data = self.to_lower_case()
        self.map_name = map_name 
        self.errors = []

    def to_lower_case(self):
        data = []
        for row_data in self.data:
            row_data["field_format"] = row_data["field_format"].lower()
            data.append(row_data)
        return data
            
    
    def is_valid_option(self, row, row_data, column, options):
        if row_data[column] not in options:
            self.add_error(row, column,
                           f"error: invalid option '{row_data[column]}' for {column}")

    def validate_unique(self):
        used_value = []
        row = 1
        for d in self.data:
            unique_column = f"{self.map_name}_{d['name']}"
            if unique_column not in used_value:
                used_value.append(unique_column)
            else:
                self.add_error(row, unique_column,
                                   f'value {d["name"]} is repeated')
            row += 1
    
    
    def validate_address(self):
        used_address = []
        row = 1
        for d in self.data:
            memory_addres = int(d["field_address"])
            if d["field_format"] in ["bitmap","boolean","uint16","sint16"]:
                size = 1
            elif d["field_format"] in ["uint32","sint32","float32"]:
                size = 2
            else:
                size = d["field_size"]
            for s in range(memory_addres, memory_addres+size):
                if s in used_address:
                    self.add_error(row, "field_address",
                           f"Duplicate address use  {memory_addres}")
                else:
                    used_address.append(s)
            row +=1
            

    def validate_modbus_data(self):
        row = 1 
        for d in self.data:
            self.is_valid_option(row, d, "field_encoding",VALID_ENCODING)
            self.is_valid_option(row, d, "field_format",VALID_FORMAT)
            self.check_valid_literal(row, d,"name")
            
            self.is_invalid_int(row, d, "field_address")
            self.is_invalid_int(row, d, "field_size")
            self.is_invalid_int(row, d, "field_offset")
            self.is_invalid_float(row,d,"field_scale")

            row +=1
      
    

    def load_csv(self):
        if Map.objects.filter(name=self.map_name):
            self.add_error(0, 0, f'map {self.map_name} is already present')
        if self.data is None or len(self.data) == 0:
             self.add_error(0, 0, 'no data in csv')
        if not self.errors:
            self.validate_column()
        if not self.errors:
            self.validate_blank_value()
        if not self.errors:
            self.validate_modbus_data()
        if not self.errors:
            self.validate_unique()
            self.validate_address()
        if not self.errors:
            self.store_csv()
        return self.errors
      
    def store_csv(self):
        maps = Map.objects.create(name=self.map_name)
        objs = []
        for data in self.data:
            data.update({
                "map":maps,
                "bit_map":BitMap.objects.get(name=data["bit_map"]) if data["bit_map"] else None,
                "min_value":None,
                "max_value":None
            })
            print(data)
            field = Field(**data)
            objs.append(field)
        Field.objects.bulk_create(objs)



class BitMapLoader(FileLoader):

    def __init__(self, data,bit_map_name):
        self.columns = BIT_MAP_COLUMN
        self.non_blank_column = BIT_MAP_NON_BLANK_COLUMN
        self.bit_map_name = bit_map_name
        self.data = data 
        self.errors = []

   
    def validate_bitmap_data(self):
        row = 1 
        for d in self.data:
            self.check_valid_literal(row, d,"ahe_name")
            row+=1

    def validate_bit_reuse(self):
        row = 1
        used_bits = []
        for data in self.data:
            start_bit = int(data["start_bit"])
            end_bit = int(data["end_bit"])
            for bit in range(start_bit, end_bit+1):
                if bit in used_bits:
                    self.add_error(row, "start_bit",
                                   f'error: bit {bit} is reused')
                else:
                    used_bits.append(bit)
            row += 1

    def validate_bit_data(self):
        row = 1
        for data in self.data:
            row_break = False

            row_break |= self.is_invalid_int(row, data, "start_bit")
            row_break |= self.is_invalid_int(row, data, "end_bit")
            if row_break:
                continue
            if int(data["start_bit"]) < 0 or int(data["start_bit"]) > 15:
                self.add_error(row, "start_bit",
                               f'error: invalid start_bit')
            if int(data["end_bit"]) < 0 or int(data["end_bit"]) > 15:
                self.add_error(row, "end_bit",
                               f'error: invalid end_bit')
            if int(data["start_bit"]) > int(data["end_bit"]):
                self.add_error(row, "start_bit",
                               f'error: end_bit is less than start_bit')
            row += 1
        if not self.errors:
            self.validate_bit_reuse()



    def store_csv(self):
        bitmap_objs = []
        bit_map = BitMap.objects.create(name=self.bit_map_name)
        for data in self.data:
            data["bit_map"] = bit_map
            bit_value = BitValue(**data)
            bitmap_objs.append(bit_value)
        BitValue.objects.bulk_create(bitmap_objs)

    def load_csv(self):
        if BitMap.objects.filter(name=self.bit_map_name):
            self.add_error(0, 0, f'Bitmap {self.bit_map_name} is already present')
        if self.data is None or len(self.data) == 0:
            self.add_error(0, 0, 'no data in csv')
        if not self.errors:
            self.validate_column()
            self.validate_blank_value()
        if not self.errors:
            self.validate_bitmap_data()
        if not self.errors:
            self.validate_bit_data()
        if not self.errors:
            self.store_csv()
        return self.errors
    
       