import ahe_translate

config = ahe_translate.models.Config.objects.first()
translate = ahe_translate.Translate(config)


data = {"voltage":1,"current":2,"battery_1_s_1_voltage":2,
        "battery_1_s_1_current":2,"battery_1_s_1_soc":3}
translate.write(data)