from dataclasses import dataclass, astuple


@dataclass
class IndicesData:
    """
    Indices of sample
    """
    __slots__ = ["MdPhi", "Mz", "QDPhi", "sigma_1", "SkqPhi", "Sk_1", "KG", "SD"]
    MdPhi: float
    Mz: float
    QDPhi: float
    sigma_1: float
    SkqPhi: float
    Sk_1: float
    KG: float
    SD: float

    def get(self) -> tuple:
        return astuple(self)


@dataclass
class SampleData:
    """
    Information about sample
    """
    __slots__ = ["collector", "performer", "sample", "location", "zone", "lat", "lon", "sampling_date"]
    collector: str
    performer: str
    sample: str
    location: str
    zone: str
    lat: str
    lon: str
    sampling_date: str
