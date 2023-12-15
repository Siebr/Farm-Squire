"""
Author: Siebrant Hendriks.

generates global data used by farm squire.
"""
from sys import argv
import re
import numpy as np
import pandas as pd


# read input files
if len(argv) > 1:
    estate_filename = argv[1]
else:
    estate_filename = 'estate_input.xlsx'
if len(argv) > 2:
    plant_filename = argv[2]
else:
    plant_filename = 'plant_input_1_cut.xlsx'
if len(argv) > 3:
    animal_filename = argv[3]
else:
    animal_filename = 'animal_input.xlsx'
if len(argv) > 4:
    biodigestor_filename = argv[4]
else:
    biodigestor_filename = 'biodigestor_input.xlsx'

estate_data = pd.read_excel(estate_filename, index_col=0)
plant_data = pd.read_excel(plant_filename, index_col=0)
animal_data = pd.read_excel(animal_filename, index_col=0)
biodigestor_data = pd.read_excel(biodigestor_filename, index_col=0)

# format input files for internal use
estate_units = estate_data['unit_of_measurement']
estate_values = estate_data['amount']

plant_units = plant_data['unit_of_measurement']
plant_data.pop('unit_of_measurement')
plant_data = plant_data.T
plant_data = plant_data.astype('float')

type_dict = {'feeding_priority': 'int',
             'bedding_use': 'bool',
             'bioprocessor_use': 'bool',
             'mulch_use': 'bool',
             'sale_use': 'bool'}
plant_data = plant_data.astype(type_dict)

unit_change = ['feed_protein_content']
plant_data[unit_change] = plant_data[unit_change] / 1000
plant_units[unit_change] = 'Kg/Kg'

animal_units = animal_data['unit_of_measurement']
animal_data.pop('unit_of_measurement')
animal_data = animal_data.T
animal_data = animal_data.astype({'initial_animal_count': 'int'})

biodigestor_units = biodigestor_data['unit_of_measurement']
biodigestor_data.pop('unit_of_measurement')
biodigestor_data = biodigestor_data.T

# calculate yearly harvest yield
grassland_ratio_total = sum(plant_data['grassland_ratio'])
cropping_ratio_total = sum(plant_data['cropping_ratio'])

plant_data['grassland_ratio'] = (plant_data['grassland_ratio'] /
                                 grassland_ratio_total)
plant_data['cropping_ratio'] = (plant_data['cropping_ratio'] /
                                cropping_ratio_total)

grassland_yields = (plant_data['grassland_ratio'] *
                    estate_values['cultivated_grasslands'] *
                    plant_data['yield_DM'])
cropping_yields = (plant_data['cropping_ratio'] *
                   estate_values['cropping_area'] *
                   plant_data['yield_DM'])

harvest_yield = np.floor(grassland_yields + cropping_yields)

# split initial herd from data
animals_on_farm = animal_data.pop('initial_animal_count')

# divide animal types in male, castrated and female
categories = ' '.join(animals_on_farm.index)
castrated_labs = re.findall(r'(?: |^)(male_castrated_\d+_year)', categories)
male_labs = re.findall(r'(?: |^)(male_\d+_year)', categories)
female_labs = re.findall(r'(?: |^)(female_\d+_year)', categories)
def sort_by_num(entry):
    number = re.search(r'\d+', entry)
    return int(number.group())
castrated_labs.sort(reverse=True, key=sort_by_num)
male_labs.sort(reverse=True, key=sort_by_num)
female_labs.sort(reverse=True, key=sort_by_num)

# calculate livestock units the farm can support
grass_size = estate_values['cultivated_grasslands']
grass_sr = estate_values['stocking_rate_grasslands']
meadow_size = estate_values['dry_meadow/field']
meadow_sr = estate_values['stocking_rate_meadow']
livestock_units_max = grass_size * grass_sr + meadow_size * meadow_sr

# initialize result dataframes
year = 1
result_init = {'revenue': '€', 'food_energy_produced': 'Kcal',
               'food_protein_produced': 'gr/Kg', 'food_fat_produced': 'gr/Kg'}
results = pd.DataFrame(result_init, index=['unit'])
new_row = pd.Series(0.0, index=results.columns, name=f'year_{year}')
results = pd.concat([results, new_row.to_frame().T], copy=False)

animals_on_farm.rename('year_1', inplace=True)
herd_results = animals_on_farm.copy().to_frame().T
