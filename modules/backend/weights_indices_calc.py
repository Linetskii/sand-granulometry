import numpy as np
from modules.backend.storage import IndicesData


class WeightsAndIndices:

    def __init__(self, fractions: np.array, weights, cfg):
        weights = np.array(weights, dtype=float)
        self.__indcs_round = cfg.indices_rounding
        self.__fractions_rounding = cfg.fractions_rounding
        self.__fractions = fractions
        self.__cumulative_weights = np.cumsum(100 * weights / sum(weights)).round(self.__fractions_rounding)
        self.__percentiles = (5, 16, 25, 50, 68, 75, 84, 95)
        self.__phi = dict(zip(self.__percentiles, np.interp(self.__percentiles, self.__cumulative_weights, fractions)))
        self.__indices = IndicesData(
            MdPhi=round(self.__phi[50], self.__indcs_round),
            Mz=round((self.__phi[16] + self.__phi[50] + self.__phi[84]) / 3, self.__indcs_round),
            QDPhi=round((self.__phi[75] - self.__phi[25]) / 2, self.__indcs_round),
            sigma_1=round((self.__phi[84] - self.__phi[16]) / 4 + (self.__phi[95] - self.__phi[5]) / 6.6,
                          self.__indcs_round),
            SkqPhi=round((self.__phi[25] + self.__phi[75] - self.__phi[50]) / 2, self.__indcs_round),
            Sk_1=round((self.__phi[16] + self.__phi[84] - 2 * self.__phi[50]) / (2 * (self.__phi[84] - self.__phi[16]))
                       + (self.__phi[5] + self.__phi[95] - 2 * self.__phi[50]) / (2 * (self.__phi[95] - self.__phi[5])),
                       self.__indcs_round),
            KG=round((self.__phi[95] - self.__phi[5]) / (2.44 * (self.__phi[75] - self.__phi[25])), self.__indcs_round),
            SD=round(self.__phi[68], self.__indcs_round)
        )

    def get(self) -> tuple:
        return self.__fractions, self.__cumulative_weights, self.__indices
