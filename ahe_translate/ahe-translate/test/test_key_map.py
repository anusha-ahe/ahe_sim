from django.test import TestCase
from ahe_translate import KeyTranslate

import json


class KeyMapTest(TestCase):

    
    def test_should_generate_key(self):
        keygen = KeyTranslate()
        keygen.get_keymap_for_variables(["abcdef"])
        key = keygen.get_key_for_var("abcdef")
        self.assertEqual(len(key), 4)

    def test_should_not_repeate_key(self):
        keygen = KeyTranslate()
        keygen.get_keymap_for_variables(["abcdef","abcdefg"])
        key1 = keygen.get_key_for_var("abcdef")
        key2 = keygen.get_key_for_var("abcdefg")
        self.assertEqual(len(key1), 4)
        self.assertEqual(len(key2), 4)
        self.assertNotEqual(key1, key2)

    def test_should_repeate_key(self):
        keygen = KeyTranslate()
        keygen.get_keymap_for_variables(["aaaaa"])
        key1 = keygen.get_key_for_var("aaaaa")
        key2 = keygen.get_key_for_var("aaaaa")
        self.assertEqual(len(key1), 4)
        self.assertEqual(len(key2), 4)
        self.assertEqual(key1, key2)
    
    def test_compute_nextkey(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey(None)
        self.assertEqual(new_key, 'A000')

    def test_compute_nextkey_1(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey('A000')
        self.assertEqual(new_key, 'A001')

    def test_compute_nextkey_2(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey('A009')
        self.assertEqual(new_key, 'A00A')

    def test_compute_nextkey_3(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey('A00Z')
        self.assertEqual(new_key, 'A010')


    def test_compute_nextkey_5(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey('A9ZZ')
        self.assertEqual(new_key, 'AA00')

    def test_compute_nextkey_6(self):
        keygen = KeyTranslate()
        new_key = keygen.compute_nextkey('AZZZ')
        self.assertEqual(new_key, 'B000')

    def test_var_from_keys(self):
        keygen = KeyTranslate()
        keygen.get_keymap_for_variables(["voltage"])
        key = keygen.get_key_for_var("voltage")
        value = keygen.get_var_for_key(key)
        self.assertEqual(value,"voltage")
    
    def test_expand_data(self):
        keygen = KeyTranslate()
        keygen.get_keymap_for_variables(["voltage","current"])
        actual_data = {"voltage":123,"current":12}
        compact_data = keygen.compact_data(actual_data)
        expand_data = keygen.expand_data(compact_data)
        self.assertEqual(expand_data,actual_data)
    
    def test_get_keymap_for_list_of_variable(self):
        keygen = KeyTranslate()
        actual_data = keygen.get_keymap_for_variables(["voltage","current","power"])
        voltage_key = keygen.get_key_for_var("voltage")
        current_key = keygen.get_key_for_var("current")
        power_key = keygen.get_key_for_var("power")
        self.assertEqual(
            [
                {"key":voltage_key,"var":"voltage"},
                {"key":current_key,"var":"current"},
                {"key":power_key,"var":"power"}

            ],actual_data)
           
   

    