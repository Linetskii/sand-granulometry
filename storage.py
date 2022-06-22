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
    # fractions: dict[str, tuple[int, float]] = (-4, -3.5, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1)

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


headers = ('Collector', 'Sampling date', 'Performer', 'Sample', 'Location', 'Latitude', 'Longitude', 'Mdφ', 'Mz',
           'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
