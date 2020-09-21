import numpy as np


class ThermodynamicParameter:
    """Observer to update HEX by changes of the X (operation parameters)"""

    def __init__(self, case_study, addresses):
        self.address_matrix = addresses.matrix
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.range_balance_utility_heat_exchangers = case_study.range_balance_utility_heat_exchangers
        self.number_hot_streams = case_study.number_hot_streams
        self.range_hot_streams = case_study.range_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.range_cold_streams = case_study.range_cold_streams
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.operating_cases = case_study.operating_cases
        self.number_enthalpy_stages = case_study.number_enthalpy_stages
        self.range_enthalpy_stages = case_study.range_enthalpy_stages
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self._heat_loads = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._enthalpy_stage_temperatures_hot_streams = np.zeros([case_study.number_hot_streams, case_study.number_enthalpy_stages + 1, case_study.number_operating_cases])
        self._enthalpy_stage_temperatures_cold_streams = np.zeros([case_study.number_cold_streams, case_study.number_enthalpy_stages + 1, case_study.number_operating_cases])
        self._temperatures_hot_stream_before_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_hot_stream_after_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_cold_stream_before_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._temperatures_cold_stream_after_hex = np.zeros([case_study.number_operating_cases, case_study.number_heat_exchangers])
        self._matrix = [self._heat_loads, self._temperatures_hot_stream_before_hex, self._temperatures_hot_stream_after_hex, self._temperatures_cold_stream_before_hex, self._temperatures_cold_stream_after_hex]
        self._value = list()

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix = value
        for callback in self._value:
            callback(self._matrix)

    def bind_to(self, callback):
        self._value.append(callback)

    @property
    def enthalpy_stage_temperatures_hot_streams(self):
        enthalpy_stage_temperatures_hot_streams = np.zeros([self.number_hot_streams, self.number_enthalpy_stages + 1, self.number_operating_cases])
        for stream in self.range_hot_streams:
            for stage in range(self.number_enthalpy_stages, -1, -1):
                enthalpy_difference = np.zeros([self.number_operating_cases])
                for operating_case in self.range_operating_cases:
                    for exchanger in self.range_heat_exchangers:
                        if self.address_matrix[exchanger, 0] == stream and \
                                self.address_matrix[exchanger, 2] == stage:
                            enthalpy_difference[operating_case] += self.matrix[0][operating_case, exchanger]
                    if stage == self.number_enthalpy_stages:
                        enthalpy_stage_temperatures_hot_streams[stream, stage, operating_case] = self.hot_streams[stream].supply_temperatures[operating_case]
                    else:
                        enthalpy_stage_temperatures_hot_streams[stream, stage, operating_case] = enthalpy_stage_temperatures_hot_streams[stream, stage + 1, operating_case] - enthalpy_difference[operating_case] / (self.hot_streams[stream].heat_capacity_flows[operating_case])
        return enthalpy_stage_temperatures_hot_streams

    @property
    def enthalpy_stage_temperatures_cold_streams(self):
        enthalpy_stage_temperatures_cold_streams = np.zeros([self.number_cold_streams, self.number_enthalpy_stages + 1, self.number_operating_cases])
        for stream in self.range_cold_streams:
            for stage in range(self.number_enthalpy_stages + 1):
                enthalpy_difference = np.zeros([self.number_operating_cases])
                for operating_case in self.range_operating_cases:
                    for exchanger in self.range_heat_exchangers:
                        if self.address_matrix[exchanger, 1] == stream and \
                                self.address_matrix[exchanger, 2] == stage - 1:
                            enthalpy_difference[operating_case] += self.matrix[0][operating_case, exchanger]
                    if stage == 0:
                        enthalpy_stage_temperatures_cold_streams[stream, stage, operating_case] = self.cold_streams[stream].supply_temperatures[operating_case]
                    else:
                        enthalpy_stage_temperatures_cold_streams[stream, stage, operating_case] = enthalpy_stage_temperatures_cold_streams[stream, stage - 1, operating_case] + enthalpy_difference[operating_case] / (self.cold_streams[stream].heat_capacity_flows[operating_case])
        return enthalpy_stage_temperatures_cold_streams

    @property
    def temperatures_hot_stream_before_hex(self):
        temperatures_hot_stream_before_hex = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            for operating_case in self.range_operating_cases:
                temperatures_hot_stream_before_hex[exchanger, operating_case] = self.enthalpy_stage_temperatures_hot_streams[self.address_matrix[exchanger, 0], self.address_matrix[exchanger, 2] + 1, operating_case]
        return temperatures_hot_stream_before_hex

    @property
    def temperatures_hot_stream_after_hex(self):
        temperatures_hot_stream_after_hex = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            for operating_case in self.range_operating_cases:
                temperatures_hot_stream_after_hex[exchanger, operating_case] = self.enthalpy_stage_temperatures_hot_streams[self.address_matrix[exchanger, 0], self.address_matrix[exchanger, 2], operating_case]
        return temperatures_hot_stream_after_hex

    @property
    def temperatures_cold_stream_before_hex(self):
        temperatures_cold_stream_before_hex = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            for operating_case in self.range_operating_cases:
                temperatures_cold_stream_before_hex[exchanger, operating_case] = self.enthalpy_stage_temperatures_cold_streams[self.address_matrix[exchanger, 1], self.address_matrix[exchanger, 2], operating_case]
        return temperatures_cold_stream_before_hex

    @property
    def temperatures_cold_stream_after_hex(self):
        temperatures_cold_stream_after_hex = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            for operating_case in self.range_operating_cases:
                temperatures_cold_stream_after_hex[exchanger, operating_case] = self.enthalpy_stage_temperatures_cold_streams[self.address_matrix[exchanger, 1], self.address_matrix[exchanger, 2] + 1, operating_case]
