from dataclasses import dataclass, astuple


@dataclass
class IndicesData:
    MdPhi: float
    Mz: float
    QDPhi: float
    sigma_1: float
    SkqPhi: float
    Sk_1: float
    KG: float
    SD: float

    def get(self):
        return astuple(self)


@dataclass
class SampleData:
    collector: str
    performer: str
    sample: str
    location: str
    zone: str
    lat: str
    lon: str
    sampling_date: str


@dataclass
class CFG:
    sep: str = ' '
    rnd_ind: int = '1'
    rnd_frac: int = '2'
    def_fract: str = 'standard'

    def update(self):
        with open('config.txt', 'r') as config:
            self.sep = config.readline().split(' = ')[1][1:-2]
            self.rnd_ind = int(config.readline().split(' = ')[1])
            self.rnd_frac = int(config.readline().split(' = ')[1])
            self.def_fract = config.readline().split(' = ')[1]

    def apply_settings(self):
        with open('config.txt', 'w') as config:
            config.write(f"sep = \'{self.sep}\'\nrnd_ind = {self.rnd_ind}\n"
                         f"rnd_frac = {self.rnd_frac}\ndef_fract = {self.def_fract}")

headers = ('Collector', 'Sampling_date', 'Performer', 'Analysis_date', 'Sample', 'Location', 'Zone',
           'Latitude', 'Longitude', 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')

sand = '\n0 to -1     Very coarse\n1 to 0      Coarse\n2 to 1      Medium\n3 to 2      Fine\n4 to 3      Very fine\n'

info = {'Mdφ': 'Median particle diameter\nMdφ = φ50' + sand,
        'Mz': 'Graphic mean particle diameter (Mz)\nMz = (φ16 + φ50 + φ84) / 3' + sand,
        'QDφ': 'Phi quartile deviation\nQDφ = (φ75 - φ25) / 2\n',
        'σ_1': 'Inclusive graphic standard deviation\nσi= (φ84 - φ16) / 4 + (φ95 - φ5) / 6.6\n'
               '<0.5    Good sorting\n0.5-1   Moderate sorting\n1<      Poor sorting\n',
        'Skqφ': 'Phi quartile skewness\nSkqφ = (φ25 + φ75 - φ50) / 2\n',
        'Sk_1': 'Inclusive graphic skewness\nSki = (φ16 + φ84 - 2φ50) / (2(φ84 - φ16)) + (φ5 + φ95 - 2φ5) / '
                '(2(φ95 - φ50))\n+0.1< fine skewed sand\n-0.1-+0.1 Near symmetry\n<-0.1 coarse skewed sand\n',
        'KG': 'Kurtosis\nKG = ((φ95 - φ5) / 2.44(φ75 - φ25)\n1.0< wide spread\n<1.0 little spread\n',
        'SD': 'Standard deviation\nSD = φ86\n'
        }
