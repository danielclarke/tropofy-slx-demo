'''
Authors: www.tropofy.com

Copyright 2014 Tropofy Pty Ltd, all rights reserved.

This source file is part of Tropofy and govered by the Tropofy terms of service
available at: http://www.tropofy.com/terms_of_service.html

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

class Box(DataSetMixin):
    box_type = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    mean_arrival_period = Column(Float, nullable=False)
    processing_time_factor = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('box_type', 'data_set_id'),)

class Processor(DataSetMixin):
    processor_number = Column(Integer, nullable=False)
    processing_time = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('processor_number', 'data_set_id'),)

class ExecuteSLX(ExecuteFunction):
    def get_button_text(self):
        return "Solve Simple Queueing Problem with SLX"

    def execute_function(self, data_set):
        call_local_solver(data_set)

    def get_table_schema(self, data_set):
        return {
            "box_type": ("string", "Box Type"),
            "priority": ("number", ""),
            "mean_arrival_period": ("number", "minutes")
        }

    def get_column_ordering(self, data_set):
        return ["box_type", "priority", "mean_arrival_period"]

class SLXSimpleQueueApp(AppWithDataSets):
    def get_name(self):
        return 'Tropofy SLX Tutorial'

    def get_gui(self):
        step_group1 = StepGroup(name='Enter your Data')
        step_group1.add_step(Step(name='Box Characteristics', widgets=[SimpleGrid(Box)]))
        step_group1.add_step(Step(name='Processor Characteristics', widgets=[SimpleGrid(Processor)]))
        step_group2 = StepGroup(name='Run Simulation')
        step_group2.add_step(Step(name='Simulate Queue', widgets=[ExecuteSLX()]))
        step_group3 = StepGroup(name='Results')
        step_group3.add_step(Step(name='Results', widgets=[]))

        return [step_group1, step_group2, step_group3]

    def get_examples(self):
        return {"Multiple Box Types": load_example_data}

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
            <p>A model of different types of boxes moving through a processing facility.</p>
            <p>This app is a proof of concept of integrating Tropofy with SLX.</p>
            ''',

            'content_row_4_col_1_content': '''
            This app was created using the <a href="http://www.tropofy.com" target="_blank">Tropofy platform</a> and is powered by SLX.
            '''
        }

def load_example_data(data_set):
    boxes = []
    boxes.append(Box(box_type="BlueBox", priority=5, mean_arrival_period=20.0, processing_time_factor=1.5))
    boxes.append(Box(box_type="GreenBox", priority=4, mean_arrival_period=7.0, processing_time_factor=1))
    boxes.append(Box(box_type="PinkBox", priority=3, mean_arrival_period=9.0, processing_time_factor=1.1))
    boxes.append(Box(box_type="YellowBox", priority=2, mean_arrival_period=15.0, processing_time_factor=0.9))
    data_set.add_all(boxes)
    processors = []
    processors.append(Processor(processor_number="0", processing_time="3.0"))
    processors.append(Processor(processor_number="1", processing_time="3.0"))
    processors.append(Processor(processor_number="2", processing_time="3.0"))
    processors.append(Processor(processor_number="3", processing_time="2.0"))
    processors.append(Processor(processor_number="4", processing_time="2.0"))
    processors.append(Processor(processor_number="5", processing_time="1.0"))
    processors.append(Processor(processor_number="6", processing_time="4.0"))
    processors.append(Processor(processor_number="7", processing_time="4.0"))
    processors.append(Processor(processor_number="8", processing_time="4.0"))
    processors.append(Processor(processor_number="9", processing_time="4.0"))
    data_set.add_all(processors)

def get_box_table_data(data_set):
    data = []
    for row in data_set.query(Box).all():
        data.append([row.box_type, row.priority, row.mean_arrival_period, row.processing_time_factor])
    return data

def get_processor_table_data(data_set):
    data = []
    for row in data_set.query(Processor).all():
        data.append([row.processor_number, row.processing_time])
    return data


def call_local_solver(data_set):
    box_dat_file_path = data_set.get_path_of_file_in_data_set_folder('box.dat')
    write_slx_box_dat_file(data_set, box_dat_file_path)

    processor_dat_file_path = data_set.get_path_of_file_in_data_set_folder('processor.dat')
    write_slx_processor_dat_file(data_set, processor_dat_file_path)

    layout_file_path = 'airport.lay'
    trace_file_path = data_set.get_path_of_file_in_data_set_folder('airport.atf')
    avi_file_path = data_set.get_path_of_file_in_data_set_folder('airport.avi')

    data_set.send_progress_message('1. Simulating scenario \n')
    invoke_slx_simulation(data_set, box_dat_file_path, processor_dat_file_path, trace_file_path)
    data_set.send_progress_message('2. Simulation finished \n')
    data_set.send_progress_message('3. Generating AVI \n')
    invoke_p3d_animation(data_set, layout_file_path, trace_file_path, avi_file_path)
    data_set.send_progress_message('4. AVI generated \n')

def write_slx_box_dat_file(data_set, box_dat_file_path):

    data = get_box_table_data(data_set)
    write_dat_file(data, box_dat_file_path)
    return box_dat_file_path

def write_slx_processor_dat_file(data_set, processor_dat_file_path):

    data = get_processor_table_data(data_set)
    write_dat_file(data, processor_dat_file_path)
    return processor_dat_file_path

def write_dat_file(data, file_path):
    f = open(file_path, 'w')

    for row in data:
        for element in row:
            f.write(str(element) + ',')
        f.write('\n')
    f.close()

    return file_path

def invoke_slx_simulation(data_set, box_dat_file_path, processor_dat_file_path, trace_file_path):
    p = subprocess.Popen(["c:\wolverine\slx\sse", "/output", "slx_output.log", "airport",
                          box_dat_file_path, processor_dat_file_path, trace_file_path],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)
    out, _ = p.communicate()

def invoke_p3d_animation(data_set, layout_file_path, trace_file_path, avi_file_path):
    p = subprocess.Popen(["c:\Wolverine\P3D\sp3d", "/MakeAVI", "1024", "768", "0", "360", layout_file_path, trace_file_path, avi_file_path],
        stdout=subprocess.PIPE,
        cwd=data_set.app.app_folder_path)
    out, _ = p.communicate()
