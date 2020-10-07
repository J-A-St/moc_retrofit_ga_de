
class Topology:
    """Heat exchanger topology data"""

    def __init__(self, exchanger_addresses, case_study, number):
        self.number = number
        # Initial heat exchanger topology
        self.initial_hot_stream = int(case_study.initial_exchanger_address_matrix['HS'][number] - 1)
        self.initial_cold_stream = int(case_study.initial_exchanger_address_matrix['CS'][number] - 1)
        self.initial_enthalpy_stage = int(case_study.initial_exchanger_address_matrix['k'][number] - 1)
        self.initial_bypass_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_hs'][number] == 1)
        self.initial_admixer_hot_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_hs'][number] == 1)
        self.initial_bypass_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['by_cs'][number] == 1)
        self.initial_admixer_cold_stream_existent = bool(case_study.initial_exchanger_address_matrix['ad_cs'][number] == 1)
        self.initial_existent = bool(case_study.initial_exchanger_address_matrix['ex'][number] == 1)

        self.exchanger_addresses = exchanger_addresses
        self.exchanger_addresses.bind_to(self.update_address_matrix)
        self.address_matrix = self.exchanger_addresses.matrix

    def update_address_matrix(self, address_matrix):
        self.address_matrix = address_matrix

    @property
    def address_vector(self):
        return self.address_matrix[self.number]

    @property
    def hot_stream(self):
        return self.address_vector[0]

    @property
    def cold_stream(self):
        return self.address_vector[1]

    @property
    def enthalpy_stage(self):
        return self.address_vector[2]

    @property
    def bypass_hot_stream_existent(self):
        return self.address_vector[3]

    @property
    def admixer_hot_stream_existent(self):
        return self.address_vector[4]

    @property
    def bypass_cold_stream_existent(self):
        return self.address_vector[5]

    @property
    def admixer_cold_stream_existent(self):
        return self.address_vector[6]

    @property
    def existent(self):
        return self.address_vector[7]

    def __repr__(self):
        pass

    def __str__(self):
        pass
