#!/usr/bin/env python3

import sys
from os import mkdir
from os.path import isfile, join, isdir, split
from pyhocon import ConfigFactory
import json

# read in a parser file and return relevant data
def read_parser(parser_file):
    hocon_file = ConfigFactory.parse_file(parser_file)
    parsers = hocon_file.get('Parsers')
    event_builders = []
    for parser in parsers:
        eb = {}
        eb['title'] = parser['Name']
        eb['name'] = parser['Name']
        eb['expression_type'] = parser['Name']
        eb['output_type'] = parser['DataType']
        eb['source'] = parser['Product']
        eb['vendor'] = parser['Vendor']
        event_builders.append(eb)
    return event_builders

# create HOCON formatted event_builder file data
def create_eventbuilder(inobject):
    outobject = []
    outobject.append('event-builder = {\n')
    outobject.append('  events = {\n')
    outobject.append('\n')
    for event in inobject:
        outobject.append('    ' + event['title'] + ' = {\n')
        outobject.append('      input-message = [{\n')
        outobject.append('        expression = "InList(type, \'' + event['expression_type'] +  '\')"\n')
        outobject.append('      }]\n')
        outobject.append('      name = ' + event['name'] + '\n')
        outobject.append('      output-type = ' + event['output_type'] + '\n')
        outobject.append('      source = ' + event['source'] + '\n')
        outobject.append('      vendor = ' + event['vendor'] + '\n')
        outobject.append('    }\n')
        outobject.append('\n')
    outobject.append('  }\n')
    outobject.append('}\n')
    return outobject

# write event_builder data to a file
def write_eventbuilder(hocon_data,outfolder):
    outfile = join(outfolder,'event_builder.conf')
    if isfile(outfile):
        print(f'WARNING: eventbuilder file "{outfile}" already exists, skipping...')
    else:
        print(f'INFO: eventbuilder file created at "{outfile}"')
        with open(outfile, 'w') as out_file:
            out_file.writelines(hocon_data)

# create manifest data from parser file
def create_manifest(inobject,name,version):
    outobject = {}
    outobject['name'] = name
    outobject['version'] = version
    outobject['minSupportedVersion'] = ["AA i54+", "DL i32+"]
    outobject['branch'] = name
    outobject['packageType'] = 'custom'
    outobject['parsers'] = []
    outobject['contentType'] = ["EventBuilders","Parsers"]
    outobject['rules'] = []
    outobject['enrichers'] = []
    outobject['parsers_mojito'] = []
    outobject['models'] = []
    outobject['readme'] = ''
    for eb in inobject:
        outobject['parsers'].append(eb['name'])
    return outobject

# write out manifest data to a json format file
def write_manifest(parser_data,outfolder):
    manifest_file = join(outfolder,'manifest.json')
    if isfile(manifest_file):
        print(f'WARNING: manifest file "{manifest_file}" already exists, skipping...')
    else:
        print(f'INFO: manifest file created at "{manifest_file}"')
        with open(manifest_file, 'w') as out_file:
            json.dump(parser_data, out_file, indent=2)

# copy parser file into target project dir
def copy_parser(parser_file,outfolder):
    outfile = join(outfolder,'parsers.conf')
    if isfile(outfile):
        print(f'WARNING: parser file "{parser_file}" already exists, skipping...')
    else:
        print(f'INFO: parser file created at "{parser_file}"')
        with open(parser_file) as open_file:
            lines = open_file.readlines()
            with open(outfile, 'w') as out_file:
                out_file.writelines(lines)

# grab folder and file from command args
target_filename = sys.argv[1]
if not isfile(target_filename):
    print(f'ERROR: target_filename "{target_filename}" does not exist or is not a feile, exiting...')
    exit()
target_folder = split(target_filename)[0:-1]
target_folder = target_folder[0]
target_file = split(target_filename)[-1]

# set up user variables
project_name = input('please input a name for the project, like c-kiteworks-custom: \n')
project_version = input('please input a version for the project, like: v1.0.3 \n')
new_foldername = project_name + '_' + project_version
project_folder = join(target_folder,new_foldername)

# create a project folder
if isdir(project_folder):
    print(f'WARNING: newdir "{project_folder}" already exists, skipping...')
else:
    mkdir(project_folder)
    print(f'INFO: newdir "{project_folder}" created...')

# read in the parser file
parser_data = read_parser(target_filename)

# output event_builder file
eb_hocon = create_eventbuilder(parser_data)
write_eventbuilder(eb_hocon,project_folder)

# output manifest file
eb_manifest = create_manifest(parser_data,project_name,project_version)
write_manifest(eb_manifest,project_folder)

# copy orig parser to target folder package
copy_parser(target_filename,project_folder)
                
