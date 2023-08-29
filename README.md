# Multi-objective evolutionary-based heat exchanger network retrofit for multi-period processes
Copyright 2023 Jan Stampfli

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4441114.svg)](https://doi.org/10.5281/zenodo.4441114)

## Description
   
   This algorithm is developed to solve the multi-objective heat exchanger network retrofit problem for multi-period processes. The customized two-level algorithm consists of a genetic algorithm for the topology optimization of the network and a differential evolution for the heat load optimization.
## License

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


## Requirements
The algorithm requires Python 3.8. The following Python modules are used:
- pandas 1.0.3
- xlrd 1.2.0 (newer versions do not support xlsx files)
- numpy 1.18.1
- scipy 1.5.0
- deap 1.3.1
## Data input
Case study data and algorithm parameters are stored in Excel spreadsheets under data. Two examples for case studies (Zweifel.xlsx and JonesP3.xlsx) as well as an algorithm parameter file (AlgorithmParameter) are provided.
## Related publications
-  Stampfli J.A., Olsen D.G., Wellig B., Hofmann R., 2020. Heat Exchanger Network Retrofit for Processes with Multiple Operating Cases: a Metaheuristic Approach, in: Proceedings of the 30th European Symposium on Computer Aided Process Engineering. Elsevier B.V., Amsterdam. volume 48, pp. 781-786. doi:[10.1016/B978-0-12-823377-1.50131-2](https://doi.org/10.1016/B978-0-12-823377-1.50131-2).
- Stampfli J.A., Ong B.H.Y., Olsen D.G., Wellig B., Hofmann R., 2022. Applied heat exchanger network retrofit for multi-period processes in industry: A hybrid evolutionary algorithm. Computers and Chemical Engineering 161, 107771. doi:[10.1016/j.compchemeng.2022.107771](https://doi.org/10.1016/j.compchemeng.2022.107771).
- Stampfli J.A., Olsen D.G., Wellig B., Hofmann R., 2022. A parallelized hybrid genetic algorithm with differential evolution for heat exchanger network retrofit. MethodsX 9, 101711. doi:[10.1016/j.mex.2022.101711](https://doi.org/10.1016/j.mex.2022.101711).
- Stampfli J.A, Ong B.H.Y., Olsen D.G., Wellig B., Hofmann R., 2023. Multi-objective evolutionary optimization for multi-period heat exchanger network retrofit. Energy 281, 128175. doi:[10.1016/j.energy.2023.128175](https://doi.org/10.1016/j.energy.2023.128175).
