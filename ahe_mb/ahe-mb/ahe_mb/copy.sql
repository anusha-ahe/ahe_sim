insert into ahe_mb_map
select name
from ahe_modbus_modbusmap amm
where name not in (
        select name
        from ahe_mb_map
    )
insert into ahe_mb_field (
        id,
        name,
        description,
        field_address,
        field_encoding,
        field_format,
        field_scale,
        field_offset,
        field_size,
        min_value,
        max_value,
        map_id
    )
select id,
    ahe_name,
    description,
    memory_address,
    encoding,
    format,
    `scale`,
    offset,
    `size`,
    NULL,
    NULL,
    modbus_map_id
from ahe_modbus_modbusfield
insert into ahe_mb_modbusdevice (
        id,
        name,
        ip_address,
        port,
        unit,
        start_address,
        register,
        max_query_size,
        data_hold_period,
        do_not_read_blank,
        map_id,
        site_id
    )
select id,
    name,
    ip_address,
    port,
    unit,
    start_address,
    register,
    query_size,
    0,
    do_not_read_blank,
    modbus_map_id,
    site_id
from ahe_modbus_device amd