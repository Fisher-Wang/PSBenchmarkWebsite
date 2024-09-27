import os


class ConfigBase:
    est_dir_name = 'est_nmap'
    upload_dir = None
    texture_names = None
    shape_names = None
    
class Config100(ConfigBase):
    dataset_dir = 'pmsData'
    upload_dir = os.path.abspath('upload_100')
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
    dataset_dir = 'pmsData_Pi'
    upload_dir = os.path.abspath('upload_Pi')
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

class ConfigRT(ConfigBase):
    dataset_dir = 'pmsData_RT'
    upload_dir = os.path.abspath('upload_RT')
    texture_names = ['']
    shape_names = [
        "imgs_T1R20",
        "imgs_T1R36",
        "imgs_T1R60",
        "imgs_T1R100",
        "imgs_T1R180",
        "imgs_T1R320",
        "imgs_T1R600",
        "imgs_T1R1200",
        "imgs_T1R3000",
        "imgs_T4R20",
        "imgs_T4R36",
        "imgs_T4R60",
        "imgs_T4R100",
        "imgs_T4R180",
        "imgs_T4R320",
        "imgs_T4R600",
        "imgs_T4R1200",
        "imgs_T4R3000",
        "imgs_T8R20",
        "imgs_T8R36",
        "imgs_T8R60",
        "imgs_T8R100",
        "imgs_T8R180",
        "imgs_T8R320",
        "imgs_T8R600",
        "imgs_T8R1200",
        "imgs_T8R3000",
        "imgs_T16R20",
        "imgs_T16R36",
        "imgs_T16R60",
        "imgs_T16R100",
        "imgs_T16R180",
        "imgs_T16R320",
        "imgs_T16R600",
        "imgs_T16R1200",
        "imgs_T16R3000",
        "imgs_T32R20",
        "imgs_T32R36",
        "imgs_T32R60",
        "imgs_T32R100",
        "imgs_T32R180",
        "imgs_T32R320",
        "imgs_T32R600",
        "imgs_T32R1200",
        "imgs_T32R3000",
        "imgs_T64R20",
        "imgs_T64R36",
        "imgs_T64R60",
        "imgs_T64R100",
        "imgs_T64R180",
        "imgs_T64R320",
        "imgs_T64R600",
        "imgs_T64R1200",
        "imgs_T64R3000",
    ]
