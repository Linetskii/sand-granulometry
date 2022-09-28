from modules.backend.singleton import SingletonMetaclass
import numpy as np
import os


class CFG(metaclass=SingletonMetaclass):
    __config = None
    """
    Config class.
    """
    __slots__ = ('separator', 'indices_rounding', 'fractions_rounding', 'fractions_scheme', 'zoomed')

    def __init__(self, root_dir):
        CFG.__config = os.path.join(root_dir, 'config.ini')
        self.separator = None
        self.indices_rounding = None
        self.fractions_rounding = None
        self.fractions_scheme = None
        self.zoomed = None
        self.__update()

    def __update(self) -> None:
        """
        Update from config.ini
        """
        with open(self.__config, 'r') as config:
            self.separator = config.readline().split(' = ')[1][1:-2]
            self.indices_rounding = int(config.readline().split(' = ')[1])
            self.fractions_rounding = int(config.readline().split(' = ')[1])
            self.fractions_scheme = config.readline().split(' = ')[1][0:-1]
            self.zoomed = 'zoomed' if config.readline().split(' = ')[1] == 'fullscreen' else 'normal'

    def apply_settings(self, sep, rnd_ind, rnd_frac, def_fract, zoomed) -> None:
        """
        Write settings to config.ini
        """
        with open(self.__config, 'w') as config:
            config.write(f"separator = \'{sep}\'\nindices_rounding = {rnd_ind}\n"
                         f"fractions_rounding = {rnd_frac}\nfractions_scheme = {def_fract}\n"
                         f"zoomed = {zoomed}")
        self.__update()


class Fractions(metaclass=SingletonMetaclass):
    __fract = None

    def __init__(self, root_dir):
        Fractions.__fract = os.path.join(root_dir, 'fractions.ini')

    @property
    def schemes(self):
        schemes = {}
        with open(self.__fract, 'r') as f:
            for line in f:
                key, value = line.split(': ')
                value = np.array(value.split(), dtype=float)
                schemes[key] = value
            return schemes

    @schemes.setter
    def schemes(self, scheme):
        with open(self.__fract, 'a') as f:
            f.write(f'\n{scheme[0]}: {scheme[1]}')
