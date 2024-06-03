import time
import ahe_log
import ahe_mb
from ahe_mb.query import ModbusQuery

def compute_query_addresses(max_query_size, addresses, read_spaces):
    '''Assumes that no variables are partially'''
    if len(addresses) == 0:
        raise ValueError("Fields are not configured for the map")

    start_address = None
    end_address = None
    query_addresses = list()
    address_list = sorted(list(addresses))
    for address in address_list:
        if start_address is not None and address - start_address >= max_query_size:
            query_addresses.append((start_address, end_address))
            start_address = None
            end_address = None
        if not read_spaces and start_address is not None and address > end_address + 1:
            query_addresses.append((start_address, end_address))
            start_address = None
            end_address = None
        if start_address is None:
            start_address = address
        end_address = address
    query_addresses.append(
        (start_address, address))
    return query_addresses


class ModbusMaster():
    def __init__(self, site_device, mode, params) -> None:
        self.params = params
        self.block = params["block_name"]
        self.logging = ahe_log.get_logger("ModbusMaster")
        self.logging.info(f"creating modbus master for {site_device} with {params}")
        if "flags" in params:
            self.flags = params["flags"].split(",")
        else:
            self.flags = []
        if type(site_device) != ahe_mb.models.SiteDevice:
            raise TypeError(
                "device should be of type ahe_mb.models.Device")
        self.site_device = site_device
        self.make_queries()
        self.next_read_query = 0

    def make_queries(self):
        device_maps =  ahe_mb.models.DeviceMap.objects.filter(device_type=self.site_device.device_type)
        for device_map in device_maps:
            all_addresses, read_spaces, map_max_read = self._list_map_addresses(device_map)
            query_addresses = compute_query_addresses(
                map_max_read, all_addresses, read_spaces)
            self.logging.debug(
                f"Address Info : {all_addresses} generated {query_addresses} queries")
            self.queries = list()
            for query_address in query_addresses:
                self.queries.append(ModbusQuery(
                    self.site_device, query_address, device_map, self.block))

    def _list_map_addresses(self, device_map):
        all_addresses = set()
        fields = device_map.map.detail.all()
        print("fields for device", fields)
        device_start_address = 0
        read_spaces = device_map.read_spaces
        map_max_read = device_map.map_max_read
        for field in fields:
            var = ahe_mb.variable.ModbusVar(field)
            for x in range(var.size):
                device_start_address = device_map.start_address
                read_spaces = device_map.read_spaces
                map_max_read = device_map.map_max_read
                absolute_address = device_start_address + field.field_address + x
                print("Address computed", absolute_address, field.field_address , x)
                if absolute_address in all_addresses:
                    raise KeyError(f"address {absolute_address} is reused")
                all_addresses.add(absolute_address)
        return all_addresses, read_spaces, map_max_read


    def read(self, epoch):
        self.logging.debug(f"read for query {self.next_read_query}")
        if self.next_read_query < 0:
            self.next_read_query = 0
            return None
        data = self.queries[self.next_read_query].read()
        self.next_read_query += 1
        if self.next_read_query >= len(self.queries):
            self.next_read_query = -1
        if not data and "data_with_epoch" in self.flags:
            return {f"{self.site_device.name}_modbus_failed": {"value": 1, "epoch": time.time()}}
        elif not data:
            return {f"{self.site_device.name}_modbus_failed": 1}
        if "data_with_epoch" in self.flags:
            data_e = dict()
            for k in data:
                data_e[k] = {"value": data[k], "epoch": data["epoch"]}
            data = data_e
            data[f"{self.site_device.name}_modbus_failed"] = {
                "value": 0, "epoch": data["epoch"]}
        data["epoch"] = epoch
        return data

    def write(self, data):
        for q in range(len(self.queries)):
            status = self.queries[q].write(data)
            if status:
                return {"status": "failed"}
        return {"status": "received"}
