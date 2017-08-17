# Author-Patrick Rainsberry
# Description-Output various items based on a csv input.


from .CSVtoOutputCommand import CSVto3dOutputCommand, CSVtoGCodeCommand, CSVtoGCodeCommand2, CSVtoGCodeCommand3

commands = []
command_definitions = []

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Fusion CSVtoGcode',
    'cmd_description': 'Import a CSV file, update model and tool paths, export g-code',
    'cmd_id': 'cmdID_CSVtoGcodeCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'class': CSVtoGCodeCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Fusion CSVtoGcode2',
    'cmd_description': 'Import a CSV file, update model and tool paths, export g-code',
    'cmd_id': 'cmdID_CSVtoGcodeCommand2',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'command_visible': False,
    'class': CSVtoGCodeCommand2
}
command_definitions.append(cmd)

# Define parameters for 3rd command
cmd = {
    'cmd_name': 'Fusion CSVtoGcode3',
    'cmd_description': 'Import a CSV file, update model and tool paths, export g-code',
    'cmd_id': 'cmdID_CSVtoGcodeCommand3',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'command_visible': False,
    'class': CSVtoGCodeCommand3
}
command_definitions.append(cmd)



# Define parameters for 3D Model Export Command
cmd = {
    'cmd_name': 'Fusion CSV to 3D Output',
    'cmd_description': 'Import a CSV file, update model and tool paths, export g-code',
    'cmd_id': 'cmdID_CSVto3dOutputCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'class': CSVto3dOutputCommand
}
command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):
    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()

