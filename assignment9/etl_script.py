import os
import sys
import arcpy
import requests
import csv

s = requests.Session()
google_form_path = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTaJ_1xRhGQAOSITkgn_C1wfPSnPX0BA37XuftlXVfVrpjfj4J3BHPu1soGeUtNt3XjLI1G_HT2Fy69/pub?output=csv'
geocode_url = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address='
geocode_suffix = '&benchmark=2020&format=json'


def pwd():
    r"""Prints the working directory.
    Used to determine the directory this module is in.
    Returns:
        The path of the directory this module is in.
    """
    wd = sys.path[0]
    arcpy.AddMessage('wd: {0}'.format(wd))
    return wd


def set_path(wd, data_path):
    r"""Joins a path to the working directory.
    Arguments:
        wd: The path of the directory this module is in.
        data_path: The suffix path to join to wd.
    Returns:
        The joined path.
    """
    path_name = os.path.join(wd, data_path)
    arcpy.AddMessage('path_name: {0}'.format(path_name))
    return path_name


def import_spatial_reference(dataset):
    r"""Extracts the spatial reference from input dataset.
    Arguments:
        dataset: Dataset with desired spatial reference.
    Returns:
        The spatial reference of any dataset input.
    """
    spatial_reference = arcpy.Describe(dataset).spatialReference
    arcpy.AddMessage('spatial_reference: {0}'.format(spatial_reference.name))
    return spatial_reference


def setup_env(workspace_path, spatial_ref_dataset):
    # Set workspace path.
    arcpy.env.workspace = workspace_path
    arcpy.AddMessage('workspace(s): {}'.format(arcpy.env.workspace))

    # Set output overwrite option.
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage('overwriteOutput: {}'.format(arcpy.env.overwriteOutput))

    # Set the output spatial reference.
    arcpy.env.outputCoordinateSystem = import_spatial_reference(
        spatial_ref_dataset)
    arcpy.AddMessage('outputCoordinateSystem: {}'.format(
        arcpy.env.outputCoordinateSystem.name))


def extract():
    # Get data
    arcpy.AddMessage('Extracting data from document')
    r = s.get(google_form_path)
    arcpy.AddMessage('HTTP Response: {0} \n {1} \n'.format(r.status_code, r.content))
    r.encoding = 'utf-8'
    data = r.text

    # Write data to csv
    arcpy.AddMessage('Writing data to addresses.csv\n')
    csv_path = os.path.join(pwd(), 'addresses.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(data)


def transform():
    arcpy.AddMessage('Transforming addresses using geocoder')

    # Create transformed csv with X, Y, and Type for headers
    csv_path = os.path.join(pwd(), 'addresses.csv')
    new_csv_path = os.path.join(pwd(), 'new_addresses.csv')
    with open(new_csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['X', 'Y', 'Type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        with open(csv_path, 'r') as address_reader:
            csv_dict = csv.DictReader(address_reader, delimiter=',')
            for row in csv_dict:
                address = '{0} {1}'.format(row['Street Address'], 'Boulder CO')
                arcpy.AddMessage('geocoding {0}'.format(address))
                url = '{0}{1}{2}'.format(geocode_url, address, geocode_suffix)
                r = s.get(url)
                resp_dict = r.json()
                x = resp_dict['result']['addressMatches'][0]['coordinates']['x']
                y = resp_dict['result']['addressMatches'][0]['coordinates']['y']
                row_dict = {'X': x, 'Y': y, 'Type': 'Residential'}
                arcpy.AddMessage('Writing row to new_addresses.csv: {0}'.format(row_dict))
                writer.writerow(row_dict)


def load():
    arcpy.AddMessage('\nCreating a point feature class from input table\n')

    # Setup local variables
    in_table = set_path(pwd(), 'new_addresses.csv')
    out_feature_class = 'avoid_points'
    x_coords = 'X'
    y_coords = 'Y'

    # Create XY event layer
    arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

    arcpy.AddMessage(
        '\nFeature class avoid_points created with {0} rows.'.format(arcpy.GetCount_management(out_feature_class)))


def main():
    # Setup Geoprocessing Environment
    spatial_ref_dataset = 'BoulderAreaTrailheads'
    wd = pwd()
    db = set_path(wd, 'GIS305Week9.gdb')
    setup_env(db, spatial_ref_dataset)

    # Extract
    extract()

    # Transform
    transform()

    # Load
    load()


if __name__ == '__main__':
    main()
