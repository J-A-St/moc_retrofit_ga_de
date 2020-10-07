import numpy as np


class ExchangerAddresses:
    """Observer to update HEX by changes of the EAM"""

    def __init__(self, case_study):
        self._matrix = np.array(case_study.initial_exchanger_address_matrix)[:, 1:9].astype(int)
        self._matrix[:, 0:3] -= 1
        self._observers = []

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix = value
        for callback in self._observers:
            callback(self._matrix)

    def bind_to(self, callback):
        self._observers.append(callback)
