from django.test import TestCase
from parameterized import parameterized
import ahe_mb
from ahe_mb.loader import BitMapLoader
from ahe_sys.common.loader import ERR_MISSING_IN_HEADER, MISSING_COLUMN_DATA, INVALID_VALUE, ALREADY_USED
import unittest


class TestLoader(TestCase):

    def _bitmap_invalid_data(self, data, error):
        bml = BitMapLoader()
        bml.load_csv(data)
        print(bml.err)
        self.assertIn(error, bml.err)

    BITMAP_MISSIG_DATA = [
        ([{}], f"bit_map {ERR_MISSING_IN_HEADER}"),
        ([{}], f"ahe_name {ERR_MISSING_IN_HEADER}"),
        ([{}], f"start_bit {ERR_MISSING_IN_HEADER}"),
        ([{}], f"end_bit {ERR_MISSING_IN_HEADER}"),
        ([{"bit_map": "", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"bit_map {MISSING_COLUMN_DATA}"),
        ([{"bit_map": "", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"ahe_name {MISSING_COLUMN_DATA}"),
        ([{"bit_map": "", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"start_bit {MISSING_COLUMN_DATA}"),
        ([{"bit_map": "", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"end_bit {MISSING_COLUMN_DATA}"),
    ]

    @parameterized.expand(BITMAP_MISSIG_DATA)
    def test_bitmap_missing_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    BITMAP_INVALID_DATA = [
        ([{"bit_map": "1", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"1 {INVALID_VALUE} bit_map"),
        ([{"bit_map": "1a", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"1a {INVALID_VALUE} bit_map"),
        ([{"bit_map": "_b", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         f"_b {INVALID_VALUE} bit_map"),

        ([{"bit_map": "b1", "ahe_name": "2", "start_bit": "",
         "end_bit": ""}], f"2 {INVALID_VALUE} ahe_name"),
        ([{"bit_map": "b1", "ahe_name": "2a", "start_bit": "",
         "end_bit": ""}], f"2a {INVALID_VALUE} ahe_name"),
        ([{"bit_map": "b1", "ahe_name": "_c", "start_bit": "",
         "end_bit": ""}], f"_c {INVALID_VALUE} ahe_name"),

        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "x",
         "end_bit": "y"}], f"x {INVALID_VALUE} start_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "x",
         "end_bit": "y"}], f"y {INVALID_VALUE} end_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "-1",
         "end_bit": "-2"}], f"-1 {INVALID_VALUE} start_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "-1",
         "end_bit": "-2"}], f"-2 {INVALID_VALUE} end_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "16",
         "end_bit": "17"}], f"16 {INVALID_VALUE} start_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "16",
         "end_bit": "17"}], f"17 {INVALID_VALUE} end_bit"),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1",
         "end_bit": "0"}], f"0 {INVALID_VALUE} end_bit"),
    ]

    @parameterized.expand(BITMAP_INVALID_DATA)
    def test_bitmap_invalid_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    BITMAP_DUPLICATE_DATA = [
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1",
             "start_bit": "1", "end_bit": "2"},
        ], f"a1 {ALREADY_USED} ahe_name"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1",
             "start_bit": "1", "end_bit": "2"},
        ], f"1 {ALREADY_USED} start_bit"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1",
             "start_bit": "1", "end_bit": "2"},
        ], f"2 {ALREADY_USED} end_bit"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "3"},
            {"bit_map": "b1", "ahe_name": "a2",
             "start_bit": "2", "end_bit": "4"},
        ], f"2-4 {ALREADY_USED} start_bit-end_bit"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "4"},
            {"bit_map": "b1", "ahe_name": "a2",
             "start_bit": "2", "end_bit": "3"},
        ], f"2-3 {ALREADY_USED} start_bit-end_bit"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "2", "end_bit": "4"},
            {"bit_map": "b1", "ahe_name": "a2",
             "start_bit": "1", "end_bit": "3"},
        ], f"1-3 {ALREADY_USED} start_bit-end_bit"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "2", "end_bit": "3"},
            {"bit_map": "b1", "ahe_name": "a2",
             "start_bit": "1", "end_bit": "4"},
        ], f"1-4 {ALREADY_USED} start_bit-end_bit"),
    ]

    @parameterized.expand(BITMAP_DUPLICATE_DATA)
    def test_bitmap_duplicate_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    VALID_BITMAP_DATA = [
        ([{"bit_map": "b1", "ahe_name": "a1_", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "a_1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "A1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "15", "end_bit": "15"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "0"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "15"}],),
    ]

    def _bitmap_valid_data(self, data):
        print("Load bitmap", data)
        bml = BitMapLoader()
        bml.load_csv(data, True)
        print(bml.err)
        self.assertEqual(0, len(bml.err))

    VALID_BITMAP_BIT_MAP = [
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "B1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1_", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b_1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
    ]

    @parameterized.expand(VALID_BITMAP_BIT_MAP)
    def test_bitmap_valid_bit_map(self, data):
        self._bitmap_valid_data(data)

    VALID_BITMAP_AHE_NAME = [
        ([{"bit_map": "b1", "ahe_name": "a1_", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "a_1", "start_bit": "1", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "A1", "start_bit": "1", "end_bit": "1"}],),
    ]

    @parameterized.expand(VALID_BITMAP_AHE_NAME)
    def test_bitmap_valid_ahe_name(self, data):
        self._bitmap_valid_data(data)

    VALID_BITMAP_BIT_START_END = [
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "1"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "15", "end_bit": "15"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "0"}],),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "15"}],),
    ]

    @parameterized.expand(VALID_BITMAP_BIT_START_END)
    def test_bitmap_valid_start_address(self, data):
        self._bitmap_valid_data(data)
