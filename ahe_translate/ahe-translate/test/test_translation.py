from django.test import TestCase
from ahe_translate import Translate
from ahe_translate.test.prepare import create_test_translation
import ahe_translate


class TestTranslation(TestCase):
    def setUp(self):
        self.config = create_test_translation("test")

    

    def test_for_single_level_hierachy(self):
        translate = ahe_translate.Translate(self.config)
        data = {"voltage": 1, "current": 2}
        process_data = translate.write(data)
        self.assertEqual(process_data["main"], {"voltage": 1})

    def test_for_multiple_field_match_for_pattern(self):
        translate = ahe_translate.Translate(self.config)
        data = {"ems_1_es_charging_limit": 95,
                "ems_1_es_discharging_limit": 10}
        process_data = translate.write(data)
        self.assertEqual(process_data["ess_main"], data)

    def test_for_multiple_level_hierachy(self):
        translate = ahe_translate.Translate(self.config)
        data = {"battery_1_voltage": 20, "battery_1_current": 30}
        process_data = translate.write(data)
        self.assertEqual(process_data["battery"], {"battery_1": data})

    def test_should_return_only_selected_fields(self):
        translate = ahe_translate.Translate(self.config)
        data = {"battery_1_voltage": 20, "battery_1_current": 30}
        process_data = translate.write(data, ["battery_1_voltage"])
        self.assertEqual(process_data["battery"], {
                         "battery_1": {"battery_1_voltage": 20}})

    def test_should_return_blank_dict_if_no_any_field_match_for_pattern(self):
        translate = ahe_translate.Translate(self.config)
        data = {"battery_1_voltage": 20, "battery_1_current": 30}
        process_data = translate.write(data)
        self.assertEqual(process_data["ess"], {})

    def test_copy_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"a_1_voltage": 30}
        process_data = translate.write(data)
        print(data, process_data)
        self.assertEqual(process_data["aux_1_voltage"], 30)

    def test_sum_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"a_voltage": 30, "b_voltage": 40, "c_voltage": 50}
        process_data = translate.write(data)
        self.assertEqual(process_data["total_voltage"], 120)

    def test_avg_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"soc_1": 30, "soc_2":15}
        process_data = translate.write(data)
        self.assertEqual(process_data["soc"], 22.5)


    def test_should_return_None_value_if_pattern_not_match(self):
        translate = ahe_translate.Translate(self.config)
        data = {"a":1}
        process_data = translate.write(data)
        self.assertEqual(process_data["test2"],None)

    
    def test_combine_func(self):
        translate = ahe_translate.Translate(self.config)
        data = {"minute":1, "hour":1}
        process_data = translate.write(data)
        self.assertEqual(process_data["merge"],"01:01")
       
    def test_adjust_func_with_adjusted_value(self):
        translate = ahe_translate.Translate(self.config)
        data = {"ess_1_active_power":1}
        process_data = translate.write(data)
        self.assertEqual(process_data["ess_1_adjusted_power"],0)

    def test_sub_func(self):
        translate = ahe_translate.Translate(self.config)
        data = {"c2_voltage":20, "c1_voltage":10}
        process_data = translate.write(data)
        self.assertEqual(process_data["voltage_diff"],10)


    def test_adjust_func_with_none_adjusted_value(self):
        translate = ahe_translate.Translate(self.config)
        data = {"ess_1_active_power":10}
        process_data = translate.write(data)
        self.assertEqual(process_data["ess_1_adjusted_power"],10)

    def test_mul_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"b1_voltage":2, "b1_current":-5}
        process_data = translate.write(data)
        self.assertEqual(process_data["power"],-10)
    
    def test_mul_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"b1_voltage":0, "b1_current":-5}
        process_data = translate.write(data)
        self.assertEqual(process_data["power"],0)
            
    def test_should_handle_None_value_for_sum(self):
        translate = ahe_translate.Translate(self.config)
        data = {"a_voltage": None, "b_voltage": None, "c_voltage": None}
        process_data = translate.write(data)
        data = {"a_voltage": None, "b_voltage": None, "c_voltage": 2}
        process_data_2 = translate.write(data)
        self.assertEqual(process_data["total_voltage"], None)
        self.assertEqual(process_data_2["total_voltage"], 2)



    def test_should_handle_None_value_for_mul(self):
        translate = ahe_translate.Translate(self.config)
        data = {"b1_voltage":None, "b1_current":None }
        process_data = translate.write(data)
        data = {"b1_voltage":None, "b1_current":2 }
        process_data_2 = translate.write(data)
        data = {"b1_voltage":None, "b1_current":0}
        process_data_3 = translate.write(data)
        data = {"b1_voltage":None, "b1_current":2}
        process_data_4 = translate.write(data)
        self.assertEqual(process_data["power"],None)
        self.assertEqual(process_data_2["power"],2)
        self.assertEqual(process_data_3["power"],0)
        self.assertEqual(process_data_4["power"],2)
    
    

    def test_should_handle_None_value_for_avg(self):
        translate = ahe_translate.Translate(self.config)
        data = {"soc_1": None, "soc_2":None}
        process_data = translate.write(data)
        data = {"soc_1": None, "soc_2":2}
        process_data_2 = translate.write(data)
        self.assertEqual(process_data["soc"], None)
        self.assertEqual(process_data_2["soc"], 2)

    def test_div_function_with_param(self):
        translate = ahe_translate.Translate(self.config)
        data = {"d2_voltage": 2000}
        process_data = translate.write(data)
        self.assertEqual(process_data["voltage_div"],2)

    def test_div_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"d3_voltage": 2000,"d4_voltage":200}
        process_data = translate.write(data)
        self.assertEqual(process_data["voltage_34_div"],10)

    def test_replace_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"module_1_cell_1": 2000}
        process_data = translate.write(data)
        self.assertEqual(process_data["m_1_cell_1"],2000)
        self.assertEqual(process_data.get("module_1_cell_1"),None)

    def test_select_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"epoch":1, "rack_1_module_1_cell_1_voltage": 3.74,"rack_1_module_1_cell_2_voltage": 3.75,"voltage":3.60}
        process_data = translate.write(data)
        self.assertEqual(process_data,{'epoch':1,'rack_1_module_1_cell_1_voltage': 3.74, 'rack_1_module_1_cell_2_voltage': 3.75})

    def test_remove_function(self):
        translate = ahe_translate.Translate(self.config)
        data = {"string_1_module_1_voltage": 3.74,"string_1_module_2_voltage": 3.75,"voltage":3.80}
        process_data = translate.write(data)
        self.assertRaises(KeyError, lambda:process_data["string_1_module_1_voltage"])
        self.assertRaises(KeyError, lambda:process_data["string_1_module_2_voltage"])

        #self.assertEqual(process_data, {"voltage":3.80})

    