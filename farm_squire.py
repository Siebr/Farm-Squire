#!/usr/bin/env python3
"""
farm squire models nutrient flows on beef farms.

coding and concept Author: Siebrant Hendriks,
data and concept Author: Millie Hookey.
Farm Squire is a script inspired by nutrient flux modelling.
It is made to model Product yields that are common for beef farms.
All the preset data relates to finnish beef farms.
"""
import global_data as gd
import feed_functions as fd
import animal_lifecycle_functions as al
import utility_functions as ul

harvest_stores = gd.harvest_yield.copy()
animals_on_farm = gd.animals_on_farm

bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
harvest_stores = harvest_stores.sub(bedding, fill_value = 0.0)
harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
# reclaim bedding if herd gets reduced during feeding?
feed = fd.feed_animals(harvest_stores, animals_on_farm)
harvest_stores -= feed
year_passes = 1
print(f'years passed: {year_passes}')
print(f'herd size is: {sum(animals_on_farm)}')
print(f'harvest_stores remain is: {int(sum(harvest_stores))}')
print(f'harvest_used is: {int(sum(gd.harvest_yield - harvest_stores))}\n')

for year_passes in range(2, 31):
    al.age_herd(animals_on_farm)
    ul.apply_stocking_limits(animals_on_farm)
    harvest_stores = gd.harvest_yield.copy()
    bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
    harvest_stores = harvest_stores.sub(bedding, fill_value = 0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    # reclaim bedding if herd gets reduced during feeding?
    feed = fd.feed_animals(harvest_stores, animals_on_farm)
    harvest_stores -= feed
    print(f'years passed: {year_passes}')
    print(f'herd size is: {sum(animals_on_farm)}')
    print(f'harvest_stores remain is: {int(sum(harvest_stores))}')
    print(f'harvest_used is: {int(sum(gd.harvest_yield - harvest_stores))}\n')

print(f'final herd is:\n{animals_on_farm}')
pass