
class Topology:
    """Heat exchanger topology data"""

    def __init__(self, case_study, number):
        # Actual heat exchanger topology
        self.hot_stream = int(case_study.initial_exchanger_address_matrix['HS'][number] - 1)
        self.cold_stream = int(case_study.initial_exchanger_address_matrix['CS'][number] - 1)
        self.enthalpy_stage = int(case_study.initial_exchanger_address_matrix['k'][number] - 1)
        self.bypass_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_hs'][number] == 1)
        self.admixer_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_hs'][number] == 1)
        self.bypass_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_cs'][number] == 1)
        self.admixer_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_cs'][number] == 1)
        self.existent = bool(case_study.initial_exchanger_address_matrix['ex'][number] == 1)
        # Initial heat exchanger topology
        self.initial_hot_stream = int(case_study.initial_exchanger_address_matrix['HS'][number] - 1)
        self.initial_cold_stream = int(case_study.initial_exchanger_address_matrix['CS'][number] - 1)
        self.initial_enthalpy_stage = int(case_study.initial_exchanger_address_matrix['k'][number] - 1)
        self.initial_bypass_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_hs'][number] == 1)
        self.initial_admixer_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_hs'][number] == 1)
        self.initial_bypass_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_cs'][number] == 1)
        self.initial_admixer_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_cs'][number] == 1)
        self.initial_existent = bool(case_study.initial_exchanger_address_matrix['ex'][number] == 1)

    @property
    def address_vector(self):
        return [self.hot_stream, self.cold_stream, self.enthalpy_stage, self.bypass_hot_stream_existent, self.admixer_hot_stream_existent, self.bypass_cold_stream_existent, self.admixer_cold_stream_existent, self.existent]

    def update_heat_exchanger_topology(self, hot_stream, cold_stream, enthalpy_stage, bypass_hot_stream_existent, admixer_hot_stream_existent, bypass_cold_stream_existent, admixer_cold_stream_existent, existent):
        self.hot_stream = hot_stream
        self.cold_stream = cold_stream
        self.enthalpy_stage = enthalpy_stage
        self.bypass_hot_stream_existent = bypass_hot_stream_existent
        self.admixer_hot_stream_existent = admixer_hot_stream_existent
        self.bypass_cold_stream_existent = bypass_cold_stream_existent
        self.admixer_cold_stream_existent = admixer_cold_stream_existent
        self.existent = existent

    def __repr__(self):
        pass

    def __str__(self):
        pass
