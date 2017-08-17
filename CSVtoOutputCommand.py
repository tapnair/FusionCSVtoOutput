import adsk.core
import adsk.fusion
import traceback

import os
from os.path import expanduser
import csv

from .Fusion360Utilities.Fusion360Utilities import get_app_objects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase
from .Fusion360Utilities.Fusion360DebugUtilities import variable_message


# Globals for multiple command execution
setup_name = None
post_name = None
output_folder = None
the_file_name = None
gcode_index = 0
gcode_test = 25
item_list = []


# Function to convert a csv file to a list of dictionaries.  Takes in one variable called "data_file_name"
def csv_dict_list(data_file_name):
    csv_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', data_file_name)

    # Open variable-based csv, iterate over the rows and map values to a list of dictionaries containing key/value pairs
    reader = csv.DictReader(open(csv_file, 'r'))
    dict_list = []
    for line in reader:
        dict_list.append(line)
    return dict_list


# Update Parameters from input values
def update_params(input_parameters):
    # Gets necessary application objects from utility function
    app_objects = get_app_objects()
    design = app_objects['design']
    units_manager = app_objects['units_manager']

    # Set all parameter values based on the input form
    for param in design.userParameters:
        new_expression = input_parameters.get(param.name, False)

        if new_expression:
            # Use Fusion Units Manager to validate user expression
            if units_manager.isValidExpression(new_expression, units_manager.defaultLengthUnits):

                # Set parameter value from input form
                param.expression = new_expression

            else:
                app_objects['ui'].messageBox("The following expression was invalid: \n" +
                                             param.name + '\n' +
                                             new_expression)


# Updates tool paths and outputs new nc file
def update_g_code(setup_name, post_name, output_folder, index):

    global gcode_index

    # TODO use app objects, probably need to switch workspaces?
    ao = get_app_objects()
    app = adsk.core.Application.get()
    doc = app.activeDocument
    products = doc.products
    product = products.itemByProductType('CAMProductType')
    cam = adsk.cam.CAM.cast(product)
    adsk.doEvents()

    # Find setup
    for setup in cam.setups:
        if setup.name == setup_name:
            to_post = setup

            # Update tool path
            future = cam.generateToolpath(to_post)
            check = 0
            while not future.isGenerationCompleted:
                adsk.doEvents()
                import time

                time.sleep(1)
                check += 1
                if check > 10:
                    ao['ui'].messageBox('Timeout')
                    break

            # Set the post options
            post_config = os.path.join(cam.genericPostFolder, post_name)
            units = adsk.cam.PostOutputUnitOptions.DocumentUnitsOutput

            program_name = setup_name + "_" + str(index)

            # create the postInput object
            post_input = adsk.cam.PostProcessInput.create(program_name, post_config, output_folder, units)
            post_input.isOpenInEditor = False

            cam.postProcess(to_post, post_input)


# Get default directory
def get_default_model_dir(model_name):

    # Get user's home directory
    default_dir = expanduser("~")

    model_name = model_name[:model_name.rfind(' v')]

    # Create a subdirectory for this application
    default_dir = os.path.join(default_dir, 'CSVtoOutput', '')

    # Create sub directory for specific model
    default_dir = os.path.join(default_dir, model_name, '')

    # Create the folder if it does not exist
    if not os.path.exists(default_dir):
        os.makedirs(default_dir)

    return default_dir


# Switch Current Workspace
def switch_workspace(workspace_name):

    ao = get_app_objects()

    workspace = ao['ui'].workspaces.itemById(workspace_name)

    workspace.activate()


def dup_check(name):
    if os.path.exists(name):
        base, ext = os.path.splitext(name)
        base += '-dup'
        name = base + ext
        dup_check(name)
    return name


def export_active_doc(folder, file_types, write_version, index):
    app = adsk.core.Application.get()
    design = app.activeProduct
    export_mgr = design.exportManager

    export_functions = [export_mgr.createIGESExportOptions,
                        export_mgr.createSTEPExportOptions,
                        export_mgr.createSATExportOptions,
                        export_mgr.createSMTExportOptions,
                        export_mgr.createFusionArchiveExportOptions,
                        export_mgr.createSTLExportOptions]
    export_extensions = ['.igs', '.step', '.sat', '.smt', '.f3d', '.stl']

    for i in range(file_types.count):

        if file_types.item(i).isSelected:

            doc_name = app.activeDocument.name

            if not write_version:
                doc_name = doc_name[:doc_name.rfind(' v')]

            export_name = folder + doc_name + '_' + str(index) + export_extensions[i]
            export_name = dup_check(export_name)
            export_options = export_functions[i](export_name)
            export_mgr.execute(export_options)

            # get_app_objects()['ui'].messageBox(export_name)


# Class for initial Model Definition and import.
class CSVtoGCodeCommand(Fusion360CommandBase):

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command, inputs, reason, input_values):
        app_objects = get_app_objects()
        next_command = app_objects['ui'].commandDefinitions.itemById('cmdID_CSVtoGcodeCommand2')
        next_command.execute()

    # This is typically where your main program logic would go
    def on_execute(self, command, inputs, args, input_values):
        global setup_name
        global post_name
        global output_folder
        global gcode_index
        global gcode_test
        global item_list

        # Get the values from the user input
        file_name = input_values['the_file_name']
        setup_name = input_values['setup_name']
        post_name = input_values['post_name']
        output_folder = input_values['output_folder']

        gcode_index = 0

        item_list = csv_dict_list(file_name)

        gcode_test = len(item_list)

        update_params(item_list[gcode_index])

    # Creates a dialog UI
    def on_create(self, command, command_inputs):

        # Create a default value using a string
        app = get_app_objects()['app']
        default_dir = get_default_model_dir(app.activeDocument.name)

        # Create a few inputs in the UI
        command_inputs.addStringValueInput('the_file_name', 'Input File: ', default_dir + 'test_csv.csv')
        command_inputs.addStringValueInput('setup_name', 'CAM Setup Name', 'Setup1')
        command_inputs.addStringValueInput('post_name', 'Post to Use:', 'validating.cps')
        command_inputs.addStringValueInput('output_folder', 'Output Folder:', default_dir)


class CSVtoGCodeCommand2(Fusion360CommandBase):

    # Update the G-Code
    def on_execute(self, command, inputs, args, input_values):
        global setup_name
        global post_name
        global output_folder
        global gcode_index
        global gcode_test

        switch_workspace('CAMEnvironment')

        update_g_code(setup_name, post_name, output_folder, gcode_index)
        switch_workspace('FusionSolidEnvironment')

        gcode_index += 1

        if gcode_index < gcode_test:
            app_objects = get_app_objects()
            next_command = app_objects['ui'].commandDefinitions.itemById('cmdID_CSVtoGcodeCommand3')
            next_command.execute()


# Class for initial Model Definition and import.
class CSVtoGCodeCommand3(Fusion360CommandBase):

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command, inputs, args, input_values):
        global setup_name
        global post_name
        global output_folder
        global the_file_name
        global item_list
        global gcode_index
        update_params(item_list[gcode_index])

        app_objects = get_app_objects()
        next_command = app_objects['ui'].commandDefinitions.itemById('cmdID_CSVtoGcodeCommand2')
        next_command.execute()


# Class for initial Model Definition and import.
class CSVto3dOutputCommand(Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command, inputs, args, input_values):
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command, inputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command_, command_inputs, changed_input, input_values):
        pass

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command, inputs, args, input_values):

        # Get the values from the user input
        file_name = input_values['the_file_name']
        folder = input_values['output_folder']
        file_types = input_values['file_types_input'].listItems
        write_version = input_values['write_version']

        item_list = csv_dict_list(file_name)

        for index, item in enumerate(item_list):
            update_params(item)
            export_active_doc(folder, file_types, write_version, index)

    # Creates a dialog UI
    def on_create(self, command, command_inputs):

        app = get_app_objects()['app']

        # Create a default value using a string
        default_dir = get_default_model_dir(app.activeDocument.name)

        # Create a few inputs in the UI
        command_inputs.addStringValueInput('the_file_name', 'Input File: ', default_dir + 'test_csv.csv')
        command_inputs.addStringValueInput('output_folder', 'Output Folder:', default_dir)

        drop_input_list = command_inputs.addDropDownCommandInput('file_types', 'Export Types',
                                                                 adsk.core.DropDownStyles.CheckBoxDropDownStyle)

        drop_input_list = drop_input_list.listItems
        drop_input_list.add('IGES', False)
        drop_input_list.add('STEP', True)
        drop_input_list.add('SAT', False)
        drop_input_list.add('SMT', False)
        drop_input_list.add('F3D', False)
        drop_input_list.add('STL', False)

        command_inputs.addBoolValueInput('write_version', 'Write versions to output file names?', True)