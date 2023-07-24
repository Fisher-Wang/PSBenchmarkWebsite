import os


class ConfigBase:
    est_dir_name = 'est_nmap'
    data_dir = os.path.abspath('tmp')
    
class Config100(ConfigBase):
    type='100'
    dataset_dir = 'pmsData'
    texture_names = [
        'POM',
        'PP',
        'NYLON',
        'PVC',
        'ABS',
        'BAKELITE',
        'Al',
        'Cu',
        'STEEL',
        'ACRYLIC',
    ]
    shape_names = [
        'BALL',
        'GOLF',
        'SPIKE',
        'NUT',
        'SQUARE',
        'PENTAGON',
        'HEXAGON',
        'PROPELLER',
        'TURBINE',
        'BUNNY',
    ]

class ConfigPi(ConfigBase):
    type='Pi'
    dataset_dir = 'pmsData_Pi'
    texture_names = ['']
    shape_names = [
        'Flower',
        'Bird',
        'Lions',
        'Rhino',
        'Queen',
        'Crab',
        'Ship',
        'Para',
        'Sail',
        'Fish',
        'Tree',
        'Ocean',
        'Lung',
        'Bear',
        'TV',
        'Sun',
        'Taichi',
        'Wave',
        'Astro',
        'Whale',
        'Bagua-T',
        'Lotus-T',
        'Lion-T',
        'Panda-T',
        'Cloud-T',
        'Bagua-R',
        'Lotus-R',
        'Lion-R',
        'Panda-R',
        'Cloud-R',
    ]