import os

import numpy as np
import pandas as pd

from heat_exchanger_network.operating_case import OperatingCase
from heat_exchanger_network.stream import Stream


class CaseStudy:
    """Reads data from case study"""

    def __init__(self, file_case_study='Jones_P3_PinCH_2.xlsx'):
        self.file = file_case_study
        self.name = file_case_study.replace('.xlsx', '')
        self.read_case_study()
        self.define_problem_dimensions()
        self.define_operating_cases()
        self.define_streams()

    def read_case_study(self):
        # Read data
        os.chdir('data')
        self.initial_exchanger_address_matrix = pd.read_excel(self.file, sheet_name='EAM')
        self.initial_exchanger_balance_utilities = pd.read_excel(self.file, sheet_name='EAM_BUT')
        self.initial_utility_balance_heat_loads = pd.read_excel(self.file, sheet_name='HeatLoads_BUT')
        self.stream_data = pd.read_excel(self.file, sheet_name='StreamData')
        self.match_cost = pd.read_excel(self.file, sheet_name='MatchCosts')
        self.economic_data = pd.read_excel(self.file, sheet_name='EconomicData')
        self.manual_parameter = pd.read_excel(self.file, sheet_name='ManualParameter')
        os.chdir('..')

    def define_problem_dimensions(self):
        # Operating cases
        self.number_operating_cases = int(max(self.stream_data['OC']))  # (-)
        self.range_operating_cases = range(self.number_operating_cases)
        # Streams
        self.number_streams = int(len(self.stream_data) / self.number_operating_cases)  # (-)
        self.range_streams = range(self.number_streams)
        self.number_hot_streams = sum(self.stream_data[0:self.number_streams]['H/C'].str.count('H'))  # (-)
        self.range_hot_streams = range(self.number_hot_streams)
        self.number_cold_streams = sum(self.stream_data[0:self.number_streams]['H/C'].str.count('C'))  # (-)
        self.range_cold_streams = range(self.number_cold_streams)
        # Enthalpy stages
        self.number_enthalpy_stages = int(max(self.initial_exchanger_address_matrix['k']))  # (-)
        self.range_enthalpy_stages = range(self.number_enthalpy_stages)
        # Heat exchangers
        self.number_heat_exchangers = len(self.initial_exchanger_address_matrix['HEX'])  # (-)
        self.range_heat_exchangers = range(self.number_heat_exchangers)
        # Balance utility heat exchangers
        self.number_balance_utility_heat_exchangers = len(self.initial_exchanger_balance_utilities['HEX'])  # (-)
        self.range_balance_utility_heat_exchangers = range(self.number_balance_utility_heat_exchangers)

    def define_operating_cases(self):
        self.operating_cases = list()
        for operating_case in self.range_operating_cases:
            self.operating_cases.append(OperatingCase(self.stream_data, operating_case, self.number_operating_cases))

    def define_streams(self):
        self.hot_streams = list()
        self.cold_streams = list()
        hot_stream = 0
        cold_stream = 0
        self.hot_utilities_indices = np.array([], dtype=int)
        self.cold_utilities_indices = np.array([], dtype=int)
        for stream in self.range_streams:
            if self.stream_data['H/C'][stream] == 'H':
                self.hot_streams.append(Stream(stream, self.number_operating_cases, self.range_operating_cases, self.number_streams, self.stream_data))
                if not np.isnan(self.stream_data['UtilityCostperkWh'][stream]):
                    self.hot_utilities_indices = np.append(self.hot_utilities_indices, hot_stream)
                hot_stream += 1
            elif self.stream_data['H/C'][stream] == 'C':
                self.cold_streams.append(Stream(stream, self.number_operating_cases, self.range_operating_cases, self.number_streams, self.stream_data))
                if not np.isnan(self.stream_data['UtilityCostperkWh'][stream]):
                    self.cold_utilities_indices = np.append(self.cold_utilities_indices, cold_stream)
                cold_stream += 1

    def __repr__(self):
        pass

    def __str__(self):
        pass
