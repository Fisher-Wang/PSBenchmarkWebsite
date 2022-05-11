import os

est_dir_name = 'est_nmap'
data_dir = os.path.abspath('tmp')

dict_show = {}

__texture_names = [
    ('pom', 'POM'), 
    ('pp', 'PP'), 
    ('nilon', 'NYLON'), 
    ('pvc', 'PVC'),
    ('abs', 'ABS'), 
    ('bakelite', 'BAKELITE'), 
    ('Al', 'Al'), 
    ('Cu', 'Cu'), 
    ('P20', 'STEEL'), 
    ('pmma', 'ACRYLIC'), 
]
default_textures = [x[0] for x in __texture_names]
default_texture_shownames = [x[1] for x in __texture_names]
#dict_show |= dict(__shape_names)    somehow wrong
for key,val in dict(__texture_names).items():
    dict_show[key] = val

__shape_names = [
    ('ball', 'BALL'),
    ('golfball', 'GOLF'),
    ('spikeball', 'SPIKE'),
    ('nutsball', 'NUT'),
    ('rhombic', 'SQUARE'),
    ('icosa', 'PENTAGON'),
    ('football', 'HEXAGON'),
    ('fans1', 'PROPELLER'),
    ('fans2', 'TURBINE'),
    ('bunny', 'BUNNY'),
]
default_shapes = [x[0] for x in __shape_names]
default_shape_shownames = [x[1] for x in __shape_names]
for key,val in dict(__shape_names).items():
    dict_show[key] = val

__method_names = [
    ('L2', 'LS'),
    ('TH28', 'TH28'),
    ('TH46', 'TH46'),
    ('WG10', 'WG10'),
    ('ST14', 'ST14'),
    ('PF14', 'PF14'),
    ('PS-FCN', 'PSFCN'),
    ('CNN-PS', 'CNNPS'),
    ('IRPS', 'IRPS'),
    ('SPLINE', 'SPLINE'),
    ('SDPS', 'SDPS'),
    ('GPS', 'GPS'),
]
default_methods = [x[0] for x in __method_names]
default_method_shownames = [x[1] for x in __method_names]
for key,val in dict(__method_names).items():
    dict_show[key] = val

default_objs = [f'{shape}_{texture}' for shape in default_shapes for texture in default_textures]

def show(name):
    return dict_show[name]