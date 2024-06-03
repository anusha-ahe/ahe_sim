from django.test import TestCase
from parameterized import parameterized
from ahe_sys.common.loader import ERR_MISSING_IN_HEADER, MISSING_COLUMN_DATA, INVALID_VALUE, ALREADY_USED
import unittest
from ahe_mb.update import BitMapUpdate
from ahe_common.serializers import FIELD_REQUIRED, FIELD_MAY_NOT_BE_BLANK, FIELD_INVALID_INT, FIELD_INVALID_VALUE, FIELD_BIT_ORDER_INVALID, FIELD_BIT_OVERLAP


class TestUpdateCsv(TestCase):

    def _bitmap_invalid_data(self, data, error):
        bml = BitMapUpdate()
        bml.load_csv(data)
        print(bml.err)
        self.assertIn(error, bml.err)

    BITMAP_MISSIG_DATA = [
        ([{}], FIELD_REQUIRED.format("bit_map")),
        ([{"bit_map": "b1"}], FIELD_REQUIRED.format("ahe_name")),
        ([{"bit_map": "b1"}], FIELD_REQUIRED.format("start_bit")),
        ([{"bit_map": "b1"}], FIELD_REQUIRED.format("end_bit")),
        # ([{"bit_map": "", "ahe_name": "", "start_bit": "", "end_bit": ""}],
        #  f"bit_map {MISSING_COLUMN_DATA}"),
        ([{"bit_map": "b1", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_MAY_NOT_BE_BLANK.format("ahe_name")),
        ([{"bit_map": "b1", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_INVALID_INT.format("start_bit")),
        ([{"bit_map": "b1", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_INVALID_INT.format("end_bit")),
    ]

    @parameterized.expand(BITMAP_MISSIG_DATA)
    def test_bitmap_missing_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    # def test_bitmap_test1(self):
    #     data = [{"bit_map": "b11", "ahe_name": "a", "start_bit": "1", "end_bit": "1"}]
    #     error = f"bit_map {ERR_MISSING_IN_HEADER}"
    #     self._bitmap_invalid_data(data, error)


    BITMAP_INVALID_DATA = [
        ([{"bit_map": "1", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_INVALID_VALUE.format("bit_map", "1")),
        ([{"bit_map": "1a", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_INVALID_VALUE.format("bit_map", "1a")),
        ([{"bit_map": "_b", "ahe_name": "", "start_bit": "", "end_bit": ""}],
         FIELD_INVALID_VALUE.format("bit_map", "_b")),

        ([{"bit_map": "b1", "ahe_name": "2", "start_bit": "",
         "end_bit": ""}], FIELD_INVALID_VALUE.format("ahe_name", "2")),

        ([{"bit_map": "b1", "ahe_name": "2a", "start_bit": "",
         "end_bit": ""}], FIELD_INVALID_VALUE.format("ahe_name", "2a")),
        ([{"bit_map": "b1", "ahe_name": "_c", "start_bit": "",
         "end_bit": ""}], FIELD_INVALID_VALUE.format("ahe_name", "_c")),

        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "x",
         "end_bit": "y"}], FIELD_INVALID_INT.format("start_bit")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "x",
         "end_bit": "y"}], FIELD_INVALID_INT.format("start_bit")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "-1",
         "end_bit": "-2"}], FIELD_INVALID_VALUE.format("start_bit", "-1")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "-1",
         "end_bit": "-2"}], FIELD_INVALID_VALUE.format("end_bit", "-2")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "16",
         "end_bit": "17"}], FIELD_INVALID_VALUE.format("start_bit", "16")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "16",
         "end_bit": "17"}], FIELD_INVALID_VALUE.format("end_bit", "17")),
        ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1",
         "end_bit": "0"}], FIELD_BIT_ORDER_INVALID.format("end_bit", "0")),
    ]

    @parameterized.expand(BITMAP_INVALID_DATA)
    def test_bitmap_invalid_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    BITMAP_DUPLICATE_DATA = [
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
        ], f"ahe_name: a1 {ALREADY_USED}"),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "1, 2")),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "2"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "1, 2")),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "3"},
            {"bit_map": "b1", "ahe_name": "a2", "start_bit": "2", "end_bit": "4"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "1, 3")),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "4"},
            {"bit_map": "b1", "ahe_name": "a2", "start_bit": "2", "end_bit": "3"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "1, 4")),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "2", "end_bit": "4"},
            {"bit_map": "b1", "ahe_name": "a2", "start_bit": "1", "end_bit": "3"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "2, 4")),
        ([
            {"bit_map": "b1", "ahe_name": "a1", "start_bit": "2", "end_bit": "3"},
            {"bit_map": "b1", "ahe_name": "a2", "start_bit": "1", "end_bit": "4"},
        ], FIELD_BIT_OVERLAP.format("end_bit", "2, 3")),
    ]

    @parameterized.expand(BITMAP_DUPLICATE_DATA)
    def test_bitmap_duplicate_data(self, data, error):
        self._bitmap_invalid_data(data, error)

    # VALID_BITMAP_DATA = [
    #     ([{"bit_map": "b1", "ahe_name": "a1_", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a_1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "A1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "15", "end_bit": "15"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "0"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "15"}],),
    # ]

    # def _bitmap_valid_data(self, data):
    #     print("Load bitmap", data)
    #     bml = BitMapLoader()
    #     bml.load_csv(data, True)
    #     print(bml.err)
    #     self.assertEqual(0, len(bml.err))

    # VALID_BITMAP_BIT_MAP = [
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "B1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1_", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b_1", "ahe_name": "a1", "start_bit": "1", "end_bit": "1"}],),
    # ]

    # @parameterized.expand(VALID_BITMAP_BIT_MAP)
    # def test_bitmap_valid_bit_map(self, data):
    #     self._bitmap_valid_data(data)

    # VALID_BITMAP_AHE_NAME = [
    #     ([{"bit_map": "b1", "ahe_name": "a1_", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a_1", "start_bit": "1", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "A1", "start_bit": "1", "end_bit": "1"}],),
    # ]

    # @parameterized.expand(VALID_BITMAP_AHE_NAME)
    # def test_bitmap_valid_ahe_name(self, data):
    #     self._bitmap_valid_data(data)

    # VALID_BITMAP_BIT_START_END = [
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "1"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "15", "end_bit": "15"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "0", "end_bit": "0"}],),
    #     ([{"bit_map": "b1", "ahe_name": "a1", "start_bit": "1", "end_bit": "15"}],),
    # ]

    # @parameterized.expand(VALID_BITMAP_BIT_START_END)
    # def test_bitmap_valid_start_address(self, data):
    #     self._bitmap_valid_data(data)
