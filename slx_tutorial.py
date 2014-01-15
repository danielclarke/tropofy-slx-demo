'''
Authors: www.tropofy.com

Copyright 2014 Tropofy Pty Ltd, all rights reserved.

This source file is part of Tropofy and govered by the Tropofy terms of service
available at: http://www.tropofy.com/terms_of_service.html

The LocalSolver this app is based on can be found at
http://www.localsolver.com/exampletour.html?file=car_sequencing.zip

Used with permission.

This source file is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.
'''

import subprocess

from sqlalchemy.types import Text, Float, Integer
from sqlalchemy.schema import Column, UniqueConstraint
from tropofy.database.tropofy_orm import DataSetMixin
from tropofy.app import AppWithDataSets, Step, StepGroup
from tropofy.widgets import ExecuteFunction, SimpleGrid

class Flight(DataSetMixin):
    flight_type = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    mean_arrival_period = Column(Float, nullable=False)
    mean_landing_time = Column(Float, nullable=False)
    color = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint('flight_type', 'data_set_id'),)

class ExecuteSLX(ExecuteFunction):
    def get_button_text(self):
        return "Solve Simple Queueing Problem with SLX"

    def execute_function(self, data_set):
        call_local_solver(data_set)
        
    def get_table_schema(self, data_set):
        return {
            "flight_type": ("string", "Flight Type"),
            "priority": ("number", ""),
            "mean_arrival_period": ("number", "minutes"),
            "mean_landing_time": ("number", "minutes"),
            "color": ("string", "")
        }

    def get_column_ordering(self, data_set):
        return ["flight_type", "priority", "mean_arrival_period", "mean_landing_time", "color"]

class SLXSimpleQueueApp(AppWithDataSets):
    def get_name(self):
        return 'SLX Simple Queue'

    def get_gui(self):
        step_group1 = StepGroup(name='Enter your Data')
        step_group1.add_step(Step(name='Flight Characteristics', widgets=[SimpleGrid(Flight)]))
        step_group2 = StepGroup(name='Run Simulation')
        step_group2.add_step(Step(name='Simulate Queue', widgets=[ExecuteSLX()]))
        step_group3 = StepGroup(name='Results')
        step_group3.add_step(Step(name='Results', widgets=[]))

        return [step_group1, step_group2, step_group3]

    def get_examples(self):
        return {"Single flight type": load_example_data}

    def get_parameters(self):
        return []


    def get_home_page_content(self):
        return {
            'content_app_name_header': '''
            <div>
            <span style="vertical-align: middle;">SLX Simple Queue</span>
            <img src="http://www.tropofy.com/static/css/img/apps/facility_location.png" alt="main logo" style="width:15%">
            </div>''',

            'content_single_column_app_description': '''
            <p>A model of different types of flights queuing in airspace and landing.</p>
            <p>This app is a proof of concept of integrating Tropofy with SLX.</p>            
            ''',

            'content_row_4_col_1_content': '''
            This app was created using the <a href="http://www.tropofy.com" target="_blank">Tropofy platform</a> and is powered by SLX.
            '''
        }

def load_example_data(data_set):
    flights = []
    flights.append(Flight(flight_type="WaterBomber", priority=100, mean_arrival_period=120.0, mean_landing_time=8.0, color="Pink"))
    flights.append(Flight(flight_type="Domestic", priority=5, mean_arrival_period=7.0, mean_landing_time=6.0, color="Blue"))
    flights.append(Flight(flight_type="International", priority=7, mean_arrival_period=12.0, mean_landing_time=9.0, color="Green"))
    flights.append(Flight(flight_type="Recreational", priority=3, mean_arrival_period=60.0, mean_landing_time=15.0, color="Yellow"))
    data_set.add_all(flights)

def get_table_data(data_set):
    data = []
    for row in data_set.query(Flight).all():
        data.append([row.flight_type, row.priority, row.mean_arrival_period, row.mean_landing_time, row.color])
    return data

def call_local_solver(data_set):
    invoke_localsolver_using_lsp_file(data_set, write_slx_input_file('airport.dat', data_set))

def write_slx_input_file(fname, data_set):
    
    data = get_table_data(data_set)
    
    f = open(fname, 'w')
    
    for row in data:
        for element in row:
            f.write(str(element) + ',')
        f.write('\n')
    f.close()
    
    return fname

def invoke_localsolver_using_lsp_file(data_set, fname):
    # Reset solution
    avi_file_path = data_set.get_path_of_file_in_data_set_folder('airport.avi')

    open(avi_file_path, 'w').close()  # clear the solution files if they exist
    
    p = subprocess.Popen(["c:\wolverine\slx\sse", "/output", "slx_output.log", "airport", fname],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)
    out, _ = p.communicate()
    
    p = subprocess.Popen(["p3dToAvi.bat"],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)