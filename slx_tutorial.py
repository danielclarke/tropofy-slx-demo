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

from tropofy.app import AppWithDataSets, Parameter, Step, StepGroup
from tropofy.widgets import ExecuteFunction, Chart, ParameterForm
from tropofy.database.tropofy_orm import DataSetMixin

class ExecuteSLX(ExecuteFunction):
    def get_button_text(self):
        return "Solve Simple Queueing Problem with SLX"

    def execute_function(self, data_set):
        call_local_solver(data_set)

class SLXSimpleQueueApp(AppWithDataSets):
    def get_name(self):
        return 'SLX Simple Queue'

    def get_gui(self):
        step_group1 = StepGroup(name='Enter your Data')
        step_group1.add_step(Step(
            name='Parameters',
            widgets=[ParameterForm()],
        ))
        step_group2 = StepGroup(name='Run Simulation')
        step_group2.add_step(Step(name='Simulate Queue', widgets=[ExecuteSLX()]))
        step_group3 = StepGroup(name='Results')
        step_group3.add_step(Step(name='Results', widgets=[]))

        return [step_group1, step_group2, step_group3]

    def get_examples(self):
        return {}

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

def call_local_solver(data_set):
    invoke_localsolver_using_lsp_file(data_set, write_slx_input_file(data_set))

def write_slx_input_file(data_set):
    pass
    '''
    input_file_path = data_set.get_path_of_file_in_data_set_folder('input.dat')    
    f = open(input_file_path, 'w')

    f.write('%s\n' % data_set.get_param('num_customers'))
    f.write('%s\n' % data_set.get_param('arrivals_per_minute'))
    f.write('%s\n' % data_set.get_param('num_tellers'))
    f.write('%s\n' % data_set.get_param('mean_service_time'))

    f.close()
    return input_file_path
    '''

def invoke_localsolver_using_lsp_file(data_set, input_file_path):
    # Reset solution
    avi_file_path = data_set.get_path_of_file_in_data_set_folder('airport.avi')

    open(avi_file_path, 'w').close()  # clear the solution files if they exist
    
    p = subprocess.Popen(["c:\wolverine\slx\sse", "airport"],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)
    out, _ = p.communicate()
    
    p = subprocess.Popen(["p3dToAvi.bat"],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)