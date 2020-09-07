import numpy as np


class ThermodynamicParameter:
    """Observer to update HEX by changes of the X (operation parameters)"""

    def __init__(self, case_study):
        self._heat_loads = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_hot_stream_before_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_hot_stream_after_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_cold_stream_before_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_cold_stream_after_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._matrix = [self._heat_loads, self._temperatures_hot_stream_before_hex, self._temperatures_hot_stream_after_hex, self._temperatures_cold_stream_before_hex, self._temperatures_cold_stream_after_hex]
        self._exchangers = list()

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix = value
        for callback in self._exchangers:
            callback(self._matrix)

    def bind_to(self, callback):
        self._exchangers.append(callback)
