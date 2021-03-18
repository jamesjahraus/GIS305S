import arcpy
import sys
import os
import time


def pwd():
    wd = sys.path[0]
    return wd


def pwd():
    wd = sys.path[0]
    return wd


def set_path(wd, data_path):
    path_name = os.path.join(wd, data_path)
    return path_name


def import_spatial_reference(dataset):
    spatial_reference = arcpy.Describe(dataset).SpatialReference
    return spatial_reference


def setup_env(workspace_path, spatial_ref_dataset):
    # Set workspace path.
    arcpy.env.workspace = workspace_path

    # Set output overwrite option.
    arcpy.env.overwriteOutput = True

    # Set the output spatial reference.
    arcpy.env.outputCoordinateSystem = import_spatial_reference(
        spatial_ref_dataset)


def check_status(result):
    r"""Function summary.
    Description sentence(s).
    Understanding message types and severity:
    https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/message-types-and-severity.htm
    Arguments:
        arg 1: Description sentence.
        arg 2: Description sentence.
    Returns:
        Description sentence.
    Raises:
        Description sentence.
    """
    status_code = dict([(0, 'New'), (1, 'Submitted'), (2, 'Waiting'),
                        (3, 'Executing'), (4, 'Succeeded'), (5, 'Failed'),
                        (6, 'Timed Out'), (7, 'Canceling'), (8, 'Canceled'),
                        (9, 'Deleting'), (10, 'Deleted')])

    arcpy.AddMessage('current job status: {0}-{1}'.format(
        result.status, status_code[result.status]))
    # Wait until the tool completes
    while result.status < 4:
        arcpy.AddMessage('current job status (in while loop): {0}-{1}'.format(
            result.status, status_code[result.status]))
        time.sleep(0.2)
    messages = result.getMessages()
    arcpy.AddMessage('job messages: {0}'.format(messages))
    return messages


def get_map(aprx, map_name):
    for mp in aprx.listMaps():
        if map_name == mp.name:
            arcpy.AddMessage('Map called {0} found'.format(mp.name))
            return mp
    arcpy.AddError('Map called {0} does not exist in current aprx {1}'.format(map_name, aprx.filePath))
    raise arcpy.ExecuteError


def intersect(layer_list, input_lyr_name, output_db):
    # Run a intersect analysis between the two buffer layers (needs to be a list of layers to intersect)
    arcpy.AddMessage('Starting Intersect Analysis')
    intersect_fc = r'{0}\{1}'.format(output_db, input_lyr_name)
    inter = arcpy.Intersect_analysis(layer_list, intersect_fc)
    check_status(inter)
    arcpy.AddMessage('Intersect Analysis Complete')
    return intersect_fc


def buffer(input_layer, dist, output_db):
    arcpy.AddMessage('Starting Buffer Analysis')
    # Run a buffer analysis on the input_layer with a user specified distance

    # Distance units are always miles
    units = " miles"
    dist = dist + units
    # Output layer will always be named input layer + "_buf
    output_fc = r'{0}\{1}{2}'.format(output_db, input_layer, '_buf')
    # Always use buffer parameters FULL, ROUND, ALL
    buf_layer = input_layer
    buf = arcpy.Buffer_analysis(buf_layer, output_fc,
                                dist, "FULL", "ROUND", "ALL")
    check_status(buf)
    arcpy.AddMessage('Buffer Analysis Complete')
    return output_fc


def layer_to_map(mp, fc, layer_name):
    arcpy.AddMessage('Adding {0} to {1}'.format(layer_name, mp.name))
    for lyr in mp.listLayers():
        if lyr.name == layer_name:
            arcpy.AddMessage('layer {0} already exists, deleting {0} ...'.format(layer_name))
            mp.removeLayer(lyr)
            break
    layer = arcpy.MakeFeatureLayer_management(fc, layer_name)
    mp.addLayer(layer[0], 'TOP')
    for lyr in mp.listLayers():
        arcpy.AddMessage(lyr.name)


def main():
    # Define your workspace and point it at the modelbuilder.gdb
    spatial_ref_dataset = 'cities'
    wd = pwd()
    input_db = set_path(wd, 'assignment8.gdb')
    output_db = set_path(wd, 'assignment8_outputs.gdb')
    setup_env(input_db, spatial_ref_dataset)

    # Map setup
    map_name = arcpy.GetParameterAsText(0)
    # map_name = 'Map'
    # aprx = arcpy.mp.ArcGISProject(r'{0}\{1}'.format(wd, 'assignment8.aprx'))
    aprx = arcpy.mp.ArcGISProject('CURRENT')
    mp = get_map(aprx, map_name)

    # Buffer cities
    # Change me this next line below to use GetParamters!!
    dist_cities = arcpy.GetParameterAsText(1)
    # dist_cities = '10'
    buf_cities = buffer('cities', dist_cities, output_db)
    arcpy.AddMessage("Buffer layer " + buf_cities + " created.")

    # Buffer rivers
    # Change me this next line below to use GetParamters!!
    dist_rivers = arcpy.GetParameterAsText(2)
    # dist_rivers = '20'
    buf_rivers = buffer('us_rivers', dist_rivers, output_db)
    arcpy.AddMessage("Buffer layer " + buf_rivers + " created.")

    # Define lyr_list variable
    # with names of input layers to intersect
    # Ask the user to define an output layer name
    # Change me this next line below to use GetParamters!!
    intersect_lyr_name = arcpy.GetParameterAsText(3)
    # intersect_lyr_name = 'model3'
    lyr_list = [buf_rivers, buf_cities]
    inter_fc = intersect(lyr_list, intersect_lyr_name, output_db)
    arcpy.AddMessage(f"New intersect layer generated called: {intersect_lyr_name}")

    # Add Layers to Map
    layer_to_map(mp, buf_cities, 'buf_cities')
    layer_to_map(mp, buf_rivers, 'buf_rivers')
    layer_to_map(mp, inter_fc, 'intersect_analysis')
    aprx.save()


if __name__ == '__main__':
    main()
