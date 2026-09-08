
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket

from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder

import qiskit_metal
from qiskit_metal import designs

design = designs.DesignPlanar()

design.chips.main.size.size_x = '12mm'
design.chips.main.size.size_y = '10mm'



            # WARNING
#options_connection_pads failed to have a value
Q1 = TransmonPocket(
design,
name='Q1',
options={'connection_pads': {'ne': {'cpw_extend': '100um',
                            'cpw_gap': 'cpw_gap',
                            'cpw_width': 'cpw_width',
                            'loc_H': 1,
                            'loc_W': 1,
                            'pad_cpw_extent': '25um',
                            'pad_cpw_shift': '5um',
                            'pad_gap': '15um',
                            'pad_height': '30um',
                            'pad_width': '125um',
                            'pocket_extent': '5um',
                            'pocket_rise': '65um'},
                     'nw': {'cpw_extend': '100um',
                            'cpw_gap': 'cpw_gap',
                            'cpw_width': 'cpw_width',
                            'loc_H': 1,
                            'loc_W': -1,
                            'pad_cpw_extent': '25um',
                            'pad_cpw_shift': '5um',
                            'pad_gap': '15um',
                            'pad_height': '30um',
                            'pad_width': '125um',
                            'pocket_extent': '5um',
                            'pocket_rise': '65um'},
                     'se': {'cpw_extend': '100um',
                            'cpw_gap': 'cpw_gap',
                            'cpw_width': 'cpw_width',
                            'loc_H': -1,
                            'loc_W': 1,
                            'pad_cpw_extent': '25um',
                            'pad_cpw_shift': '5um',
                            'pad_gap': '15um',
                            'pad_height': '30um',
                            'pad_width': '125um',
                            'pocket_extent': '5um',
                            'pocket_rise': '65um'},
                     'sw': {'cpw_extend': '100um',
                            'cpw_gap': 'cpw_gap',
                            'cpw_width': 'cpw_width',
                            'loc_H': -1,
                            'loc_W': -1,
                            'pad_cpw_extent': '25um',
                            'pad_cpw_shift': '5um',
                            'pad_gap': '15um',
                            'pad_height': '30um',
                            'pad_width': '125um',
                            'pocket_extent': '5um',
                            'pocket_rise': '65um'}},
 'pad_width': '425um',
 'pos_x': '0mm',
 'pos_y': '0mm'}
)





            # WARNING
#options_connection_pads failed to have a value
Q2 = TransmonPocket(
design,
name='Q2',
options={'connection_pads': {'p': {'cpw_extend': '100um',
                           'cpw_gap': 'cpw_gap',
                           'cpw_width': 'cpw_width',
                           'loc_H': -1,
                           'loc_W': -1,
                           'pad_cpw_extent': '25um',
                           'pad_cpw_shift': '5um',
                           'pad_gap': '15um',
                           'pad_height': '30um',
                           'pad_width': '125um',
                           'pocket_extent': '5um',
                           'pocket_rise': '65um'}},
 'pad_width': '425um',
 'pos_x': '1.061mm',
 'pos_y': '1.061mm'}
)





            # WARNING
#options_connection_pads failed to have a value
Q3 = TransmonPocket(
design,
name='Q3',
options={'connection_pads': {'p': {'cpw_extend': '100um',
                           'cpw_gap': 'cpw_gap',
                           'cpw_width': 'cpw_width',
                           'loc_H': -1,
                           'loc_W': 1,
                           'pad_cpw_extent': '25um',
                           'pad_cpw_shift': '5um',
                           'pad_gap': '15um',
                           'pad_height': '30um',
                           'pad_width': '125um',
                           'pocket_extent': '5um',
                           'pocket_rise': '65um'}},
 'pad_width': '425um',
 'pos_x': '-1.061mm',
 'pos_y': '1.061mm'}
)





            # WARNING
#options_connection_pads failed to have a value
Q4 = TransmonPocket(
design,
name='Q4',
options={'connection_pads': {'p': {'cpw_extend': '100um',
                           'cpw_gap': 'cpw_gap',
                           'cpw_width': 'cpw_width',
                           'loc_H': 1,
                           'loc_W': 1,
                           'pad_cpw_extent': '25um',
                           'pad_cpw_shift': '5um',
                           'pad_gap': '15um',
                           'pad_height': '30um',
                           'pad_width': '125um',
                           'pocket_extent': '5um',
                           'pocket_rise': '65um'}},
 'pad_width': '425um',
 'pos_x': '-1.061mm',
 'pos_y': '-1.061mm'}
)





            # WARNING
#options_connection_pads failed to have a value
Q5 = TransmonPocket(
design,
name='Q5',
options={'connection_pads': {'p': {'cpw_extend': '100um',
                           'cpw_gap': 'cpw_gap',
                           'cpw_width': 'cpw_width',
                           'loc_H': 1,
                           'loc_W': -1,
                           'pad_cpw_extent': '25um',
                           'pad_cpw_shift': '5um',
                           'pad_gap': '15um',
                           'pad_height': '30um',
                           'pad_width': '125um',
                           'pocket_extent': '5um',
                           'pocket_rise': '65um'}},
 'pad_width': '425um',
 'pos_x': '1.061mm',
 'pos_y': '-1.061mm'}
)




route_Q1_Q2 = RoutePathfinder(
design,
name='route_Q1_Q2',
options={'_actual_length': '0.8390796326794896 '
                   'mm',
 'fillet': '50um',
 'lead': {'end_jogged_extension': '',
          'end_straight': '100um',
          'start_jogged_extension': '',
          'start_straight': '100um'},
 'pin_inputs': {'end_pin': {'component': 'Q2',
                            'pin': 'p'},
                'start_pin': {'component': 'Q1',
                              'pin': 'ne'}},
 'trace_gap': '6um',
 'trace_width': '10um'},

type='CPW',
)




route_Q1_Q3 = RoutePathfinder(
design,
name='route_Q1_Q3',
options={'_actual_length': '0.8390796326794896 '
                   'mm',
 'fillet': '50um',
 'lead': {'end_jogged_extension': '',
          'end_straight': '100um',
          'start_jogged_extension': '',
          'start_straight': '100um'},
 'pin_inputs': {'end_pin': {'component': 'Q3',
                            'pin': 'p'},
                'start_pin': {'component': 'Q1',
                              'pin': 'nw'}},
 'trace_gap': '6um',
 'trace_width': '10um'},

type='CPW',
)




route_Q1_Q4 = RoutePathfinder(
design,
name='route_Q1_Q4',
options={'_actual_length': '0.8390796326794896 '
                   'mm',
 'fillet': '50um',
 'lead': {'end_jogged_extension': '',
          'end_straight': '100um',
          'start_jogged_extension': '',
          'start_straight': '100um'},
 'pin_inputs': {'end_pin': {'component': 'Q4',
                            'pin': 'p'},
                'start_pin': {'component': 'Q1',
                              'pin': 'sw'}},
 'trace_gap': '6um',
 'trace_width': '10um'},

type='CPW',
)




route_Q1_Q5 = RoutePathfinder(
design,
name='route_Q1_Q5',
options={'_actual_length': '0.8390796326794896 '
                   'mm',
 'fillet': '50um',
 'lead': {'end_jogged_extension': '',
          'end_straight': '100um',
          'start_jogged_extension': '',
          'start_straight': '100um'},
 'pin_inputs': {'end_pin': {'component': 'Q5',
                            'pin': 'p'},
                'start_pin': {'component': 'Q1',
                              'pin': 'se'}},
 'trace_gap': '6um',
 'trace_width': '10um'},

type='CPW',
)



design.rebuild()
