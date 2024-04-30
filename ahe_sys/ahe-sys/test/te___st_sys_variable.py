from django.test import TestCase
from ahe_sys.models import Variable, DeviceType
from ahe_sys.views import create_vatiable, SiteUpdate, SiteDeviceUpdate
import json
import re

SITE_NAME_TEST = "test runner site 1"
SITE_ID_TEST = 999
SITE_DATA = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST}


def translate_device(device_name):
    return device_name.replace("_", " ").upper()


fixed_translations = {"Soc$": "SoC",
                      " Soc ": " SoC ",
                      "Soh$": "SoH",
                      "Module$": "Module Num",
                      "Cell$": "Cell Num",
                      "Time To Full Discharge": "Full Discharge Time",
                      "Time To Full Charge": "Full Charge Time",
                      "Cycle Count": "Cycles",
                      "Setpoint": "SetPoint",
                      "Es ": "ES Mode ",
                      "Man ": "Manual Mode ",
                      "ES Charging": "ES Mode Charging",
                      "ES Discharging": "ES Mode Discharging",
                      "Dc ": "DC ",
                      "Heatsink": "HeatSink",
                      "Igbt": "igbt",
                      "Phase ": "Ph",
                      "Ess ": "ESS "
                      }


def translate_var(var_name):
    # if var_name in fixed_translations:
    #     return fixed_translations[var_name]
    v_name = list()
    for name in var_name.split("_"):
        if name in fixed_translations:
            name = fixed_translations[name]
        else:
            name = name.capitalize()
        v_name.append(name)
    var_name = " ".join(v_name)
    for k in fixed_translations:
        var_name = re.sub(k, fixed_translations[k], var_name)
    return var_name


class TestSiteVariable(TestCase):
    def te_st_variable_create(self):
        su = SiteUpdate()
        test_site = su.update(SITE_DATA)
        sdu = SiteDeviceUpdate()
        dev = DeviceType.objects.filter(name="delta").first()
        sdu.add_site_device(test_site.id, dev.id)
        dev = DeviceType.objects.filter(name="EOS").first()
        sdu.add_site_device(test_site.id, dev.id)

        with open("./list_of_item/5.json") as fi:
            data = json.load(fi)
        for d in data:
            print(d, data[d])

            var = create_vatiable(test_site, d)
            self.assertIsNotNone(var, "var could not be created")
            self.assertEqual(var.source.device_name, data[d]["source"])
            self.assertEqual(var.med_name, data[d]["med_name"])
            self.assertEqual(var.long_name, data[d]["long_name"])
            # self.assertEqual(var.require_in_frontend,
            #                  data[d]["require_in_frontend"])
            self.assertEqual(var.measurement_unit, data[d]["unit"])
            self.assertEqual(var.decimal_places, data[d]["decimals"])
            # self.assertEqual(var.category, data[d]["category"])

    PATTERN_LIST = ['^battery_(\d+)_rack_(\d+)',
                    '^battery_(\d+)',
                    '^ems_(\d+)',
                    '^inverter_(\d+)',
                    '^dc_meter_(\d+)',
                    ]
    file_list = ["./list_of_item/5.json", "./list_of_item/10.json"]

    def te_st_variable_create(self):
        data_ctr = 0
        for file in self.file_list:
            with open(file) as fi:
                data = json.load(fi)
            for d in data:

                if data[d]["source"] == "main":
                    continue
                data_ctr += 1
                print(data_ctr, d, data[d])
                checked = False
                for pattern in self.PATTERN_LIST:
                    pn = re.compile(pattern)
                    res = pn.search(d)
                    if not res:
                        continue
                    device_name = res.group()
                    # device_name_upper = translate_device(device_name)
                    var_name = d[res.span()[1] + 1:]
                    var_name_tran = translate_var(var_name)
                    print(data[d]["med_name"])
                    print(var_name_tran)
                    self.assertEqual(data[d]["med_name"], var_name_tran)
                    checked = True
                    break
                self.assertTrue(checked)
            # self.fail("")
