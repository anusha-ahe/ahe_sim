from ahe_translate.models import Node, Hirarchy, NodeVariable,Config,Translation
from ahe_sys.update import create_site_args

def create_test_hirarchy(node_params):
    Hirarchy.objects.filter(name="test_hirarchy").delete()
    hirarchy = Hirarchy(name="test_hirarchy")
    hirarchy.save()
    nodes = []
    node = None
    for np in node_params:
        node = create_test_node(
            hirarchy, np["name"], np["count"], np["pattern"], node)
        nodes.append(node)
        for variable in np["variables"]:
            NodeVariable(variable=variable, parent=node).save()
    return hirarchy, nodes


def create_test_node(hirarchy, name, node_count, pattern, parent):
    node_data = {"name": name, "hirarchy": hirarchy, "pattern": pattern,
                 "has_variables": True,  "count": node_count, "parent": parent}
    new_node = Node(**node_data)
    new_node.save()
    return new_node

def create_test_translation(name):
    site = create_site_args(id=881, name="test")
    config = Config(site=site,name=name)
    config.save()
    translation = Translation(seq=1,source="^voltage",dest="main",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=2,source="^ems_1_es_",dest="ess_main",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=3,source="^battery_1",dest="battery_1",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=3,source="^battery_2",dest="battery_1",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=3,source="^battery_3",dest="battery_1",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=4,source="^battery_1$",dest="battery",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=5,source="^ess_1$",dest="ess",
                            func="HIERACHY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=6,source="a_1_voltage",dest="aux_1_voltage",
                            func="COPY",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=7,source="^(a_voltage|b_voltage|c_voltage)",dest="total_voltage",
                            func="SUM",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=8,source="^(soc_1|soc_2)",dest="soc",
                            func="AVG",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=9,source="^test_1",dest="test2",
                            func="AVG",config=config,removed_match=0)
    translation.save()
   
    translation = Translation(seq=10,source="^(minute|hour)",dest="merge",
                            func="COMBINE",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=11,source="ess_1_active_power",dest="ess_1_adjusted_power",
                            func="ADJUST",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=11,source="(b1_voltage|b1_current)",dest="power",
                            func="MUL",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=12,source="(c2_voltage|c1_voltage)",dest="voltage_diff",
                            func="SUB",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=13,source="d2_voltage",dest="voltage_div",
                            func="DIV",param=1000,config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=14,source="(d3_voltage|d4_voltage)",dest="voltage_34_div",
                            func="DIV",config=config,removed_match=0)
    translation.save()
    translation = Translation(seq=15,source="^module_1_cell_1$",dest="module_1_cell_1",
                            func="REPLACE",config=config,removed_match=0,param="module_1,m_1")
    translation.save()
    translation = Translation(seq=16,source="^rack_1_module_",dest="cell_data",
                            func="SELECT",config=config,removed_match=0)
    translation.save()
    
    translation = Translation(seq=17,source="^string_1_module_",dest="cell_data",
                            func="REMOVE",config=config,removed_match=0)
    translation.save()
    return config
