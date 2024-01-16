"""
Author: Siebrant Hendriks.

generates global data used by farm squire.
"""
from sys import argv
import re
import numpy as np
import pandas as pd


print('startup, please wait...')
# read input file, defaults to example if no other file is given.
if len(argv) > 1:
    FILENAME = argv[1]
else:
    FILENAME = 'input_example.xlsx'
input_file = pd.ExcelFile(FILENAME)

estate_data = pd.read_excel(input_file, sheet_name='estate', index_col=0)
plant_data = pd.read_excel(input_file, sheet_name='crops', index_col=0)
animal_data = pd.read_excel(input_file, sheet_name='animal', index_col=0)
biodigestor_data = pd.read_excel(input_file, sheet_name='biodigestor',
                                 index_col=0)
input_file.close()

estate_data_ori = estate_data.copy()
plant_data_ori = plant_data.copy()
animal_data_ori = animal_data.copy()
biodigestor_data_ori = biodigestor_data.copy()

# format input files for internal use
estate_units = estate_data['unit_of_measurement']
estate_values = estate_data['amount']

plant_units = plant_data.pop('unit_of_measurement')
plant_data = plant_data.T
plant_data = plant_data.astype('float')

type_dict = {'feeding_priority': 'int',
             'bedding_use': 'bool',
             'bioprocessor_use': 'bool',
             'mulch_use': 'bool',
             'sale_use': 'bool'}
plant_data = plant_data.astype(type_dict)

UNIT_CHANGE = 'feed_protein_content'
plant_data[UNIT_CHANGE] = plant_data[UNIT_CHANGE] / 1000
plant_units[UNIT_CHANGE] = 'Kg/Kg'

animal_units = animal_data.pop('unit_of_measurement')
animal_data = animal_data.T
animal_data = animal_data.astype({'initial_animal_count': 'int'})

biodigestor_units = biodigestor_data.pop('unit_of_measurement')
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
harvest_yield = harvest_yield.astype('int')

# calculate yearly flat crop money balance
grassland_ha = plant_data['grassland_ratio'] *\
    estate_values['cultivated_grasslands']
cropping_ha = plant_data['cropping_ratio'] *\
    estate_values['cropping_area']
harvest_ha = grassland_ha + cropping_ha
crop_balance = sum(plant_data['subsidies'] * harvest_ha)
crop_balance -= estate_values['rented_land'] * estate_values['land_rent']
crop_balance -= sum(harvest_yield * plant_data['cultivation_costs'])
crop_balance -= sum(harvest_yield * plant_data['contract_work_costs'])
labour = sum(harvest_yield * plant_data['general_labour_needed'])
regular_labour_avail = estate_values['max_yearly_regular_labour']
if labour > regular_labour_avail:
    labour -= regular_labour_avail
    labour_cost = regular_labour_avail * estate_values['regular_labour_cost']
    labour_cost += labour * estate_values['casual_labour_cost']
else:
    labour_cost = labour * estate_values['regular_labour_cost']
crop_balance -= labour_cost
fuel_use = estate_values['fuel_use_harvester_grassland'] *\
    estate_values['cultivated_grasslands']
fuel_use += estate_values['fuel_use_harvester_meadow'] *\
    estate_values['dry_meadow/field']
fuel_use += estate_values['fuel_use_harvester_cropping'] *\
    estate_values['cropping_area']
fuel_cost = fuel_use * estate_values['fuel_price']
crop_balance -= fuel_cost

# check brewery
brewery = False
if harvest_ha['Barley'] + harvest_ha['Barley_straw'] >=\
        estate_values['BSG/BSY_from_barley_only_at']:
    brewery = True
if brewery:
    harvest_yield['BS_grain'] = int(np.floor(estate_values['import_BSG_DM']))
    harvest_yield['BS_yeast'] = int(np.floor(estate_values['import_BSY_DM']))

# calculate yearly phosphorus and nitrogen needed to fertilize crops
p_use = 0.0
n_use = 0.0
for label, amount in harvest_yield.items():
    p_use += plant_data['P_content'].loc[label] * amount
    n_use += plant_data['N_content'].loc[label] * amount

# make intermediate pd.Series used for tracking nitrogen and phosphorus changes
fertile_molecules = pd.Series(0.0, index=['phosphorus', 'nitrogen'])

# split initial herd from data
animals_on_farm = animal_data.pop('initial_animal_count')

# divide animal types in male, castrated and female
CATEGORIES = ' '.join(animals_on_farm.index)
castrated_labs = re.findall(r'(?: |^)(male_castrated_\d+_year)', CATEGORIES)
male_labs = re.findall(r'(?: |^)(male_\d+_year)', CATEGORIES)
female_labs = re.findall(r'(?: |^)(female_\d+_year)', CATEGORIES)
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
result_init = {'revenue_balance_animal': '€', 'revenue_balance_crops': '€',
               'food_energy_produced': 'Kcal',
               'food_protein_produced': 'gr/Kg', 'food_fat_produced': 'gr/Kg',
               'electricity_balance': 'MJ', 'digestate_produced': 'Kg',
               'biomethane_produced': 'g_CH4', 'phosphorus_balance': 'g_P',
               'nitrogen_balance': 'g_N',
               'digestion_methane_emissions': 'g_CH4',
               'manure_methane_emissions': 'g_CH4'}
results = pd.DataFrame(result_init, index=['unit'])
new_row = pd.Series(0.0, index=results.columns, name=f'year_{year}')
results = pd.concat([results, new_row.to_frame().T], copy=False)

animals_on_farm.rename('year_1', inplace=True)
herd_results = animals_on_farm.copy().to_frame().T

crops_sold = pd.DataFrame()
feed_used = pd.DataFrame()
digestor_used = pd.DataFrame()
mulch_used = pd.DataFrame()
bedding_used = pd.DataFrame()

print('startup complete\n')


if __name__ == '__main__':
    print('This is only a supplementary script to "farm_squire.py".')
    print('This script takes the input files supplied by the command line' +
          ' and reads those in.')
    print(f'The current files used are: {FILENAME}')
