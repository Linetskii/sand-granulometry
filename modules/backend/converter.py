import numpy as np


class ConvertUnits:
    def __init__(self, inp, unit1, unit2, separator):
        self.__inp = np.array(inp, dtype=float)
        self.__unit1 = unit1
        self.__unit2 = unit2
        self.__separator = separator

    def mm_phi(self):
        return f'{self.__separator}'.join(map(str, np.around(-np.log2(self.__inp), 2)))  # -log2(x, mm)

    def mm_mu(self):
        return f'{self.__separator}'.join(map(str, self.__inp * 1000))  # x,mm * 1000 / 2

    def phi_mm(self):
        return f'{self.__separator}'.join(map(str, np.around(1 / (2 ** self.__inp), 2)))  # 1 / (2^x,phi)

    def phi_mu(self):
        return f'{self.__separator}'.join(map(str, np.around(1000 / (2 ** self.__inp), 2)))  # 1000 / 2^x,phi

    def mu_phi(self):
        return f'{self.__separator}'.join(map(str, np.around(-np.log2(0.001 * self.__inp), 2)))  # -log2(x,mu / 1000)

    def mu_mm(self):
        return f'{self.__separator}'.join(map(str, np.around(0.001 * self.__inp, 2)))  # x,mu / 1000

    def calculate(self):
        if self.__unit1 == "mm":
            if self.__unit2 == "φ":
                return self.mm_phi()
            if self.__unit2 == "μ":
                return self.mm_mu()
        if self.__unit1 == "φ":
            if self.__unit2 == "mm":
                return self.phi_mm()
            if self.__unit2 == "μ":
                return self.phi_mu()
        if self.__unit1 == "μ":
            if self.__unit2 == "mm":
                return self.mu_mm()
            if self.__unit2 == "φ":
                return self.mu_phi()
