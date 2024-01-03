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
import pandas as pd
import feed_functions as fd
import animal_lifecycle_functions as al
import utility_functions as ul
import bioprocessor_functions as bi


if __name__ == '__main__':
    harvest_stores = gd.harvest_yield.copy()
    animals_on_farm = gd.animals_on_farm
    ul.fixate_fm(harvest_stores)
    bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
    harvest_stores = harvest_stores.sub(bedding, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    # reclaim bedding if herd gets reduced during feeding?
    feed = fd.feed_animals(harvest_stores, animals_on_farm)
    harvest_stores -= feed
    biomatter_available = bi.biopro_all(harvest_stores, animals_on_farm)
    biomatter_use = bi.biopro_to_use(biomatter_available)
    ul.extract_fm(biomatter_use)
    bi.make_biopro_products(biomatter_use)
    harvest_stores = harvest_stores.sub(biomatter_use, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    cash_crops = ul.select_cash_crops(harvest_stores)
    ul.apply_cash_crop_yield(cash_crops)
    harvest_stores = harvest_stores.sub(cash_crops, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    ul.fertilize_fm()
    ul.report_and_wipe_fm()
    
    
    print(f'years passed: {gd.year}')
    print(f'herd size is: {sum(animals_on_farm)}\n')

    
    while gd.year < gd.estate_values['runtime']:
        gd.year += 1
        new_row = pd.Series(0.0, index=gd.results.columns,
                            name=f'year_{gd.year}')
        gd.results = pd.concat([gd.results, new_row.to_frame().T], copy=False)
        al.age_herd(animals_on_farm)
        ul.apply_stocking_limits(animals_on_farm)
        harvest_stores = gd.harvest_yield.copy()
        ul.fixate_fm(harvest_stores)
        bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
        harvest_stores = harvest_stores.sub(bedding, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        # reclaim bedding if herd gets reduced during feeding?
        feed = fd.feed_animals(harvest_stores, animals_on_farm)
        harvest_stores -= feed
        biomatter_available = bi.biopro_all(harvest_stores, animals_on_farm)
        biomatter_use = bi.biopro_to_use(biomatter_available)
        ul.extract_fm(biomatter_use)
        bi.make_biopro_products(biomatter_use)
        harvest_stores = harvest_stores.sub(biomatter_use, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        cash_crops = ul.select_cash_crops(harvest_stores)
        ul.apply_cash_crop_yield(cash_crops)
        harvest_stores = harvest_stores.sub(cash_crops, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        ul.fertilize_fm()
        ul.report_and_wipe_fm()
        animals_on_farm.rename(f'year_{gd.year}', inplace=True)
        gd.herd_results = pd.concat([gd.herd_results,
                                     animals_on_farm.to_frame().T], copy=False)
        print(f'years passed: {gd.year}')
        print(f'herd size is: {sum(animals_on_farm)}\n')
    
    print(f'final herd is:\n{animals_on_farm}')
    
    with pd.ExcelWriter('squire_results.xlsx') as writer:
        gd.results.to_excel(writer, sheet_name='statistics')
        gd.herd_results.to_excel(writer, sheet_name='herd')
    pass
