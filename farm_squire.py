#!/usr/bin/env python3
"""
farm squire models nutrient flows and yearly operations on beef farms.

coding and concept Author: Siebrant Hendriks,
data and concept Author: Millie Hookey.
Farm Squire is a script inspired by nutrient flux modelling.
It is made to model Product yields that are common for beef farms.
All the preset data relates to finnish beef farms.
"""
import os
import datetime as dt
import pandas as pd
import global_data as gd
import feed_functions as fd
import animal_lifecycle_functions as al
import utility_functions as ul
import bioprocessor_functions as bi

# Core loop implemented as 'do while' each run accounts for one year of
# operations.
if __name__ == '__main__':
    print('simulating...')
    harvest_stores = gd.harvest_yield.copy()
    ul.apply_crop_balance()
    animals_on_farm = gd.animals_on_farm
    ul.fixate_fm(harvest_stores)
    bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
    ul.report_bedding(bedding)
    harvest_stores = harvest_stores.sub(bedding, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    # reclaim bedding if herd gets reduced during feeding?
    feed = fd.feed_animals(harvest_stores, animals_on_farm)
    ul.report_feed(feed)
    harvest_stores -= feed
    ul.apply_digestion_methane_emission(animals_on_farm)
    manure = animals_on_farm * gd.animal_data['manure_pasture_production']
    ul.apply_manure(manure)
    biomatter_available = bi.biopro_all(harvest_stores, animals_on_farm)
    biomatter_use = bi.biopro_to_use(biomatter_available)
    ul.report_digestor(biomatter_use)
    ul.extract_fm(biomatter_use)
    bi.make_biopro_products(biomatter_use)
    ul.apply_digestate()
    harvest_stores = harvest_stores.sub(biomatter_use, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    mulch = ul.select_mulch(harvest_stores, biomatter_available, biomatter_use)
    ul.report_mulch(mulch)
    ul.apply_mulch(mulch)
    harvest_stores = harvest_stores.sub(mulch, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    cash_crops = ul.select_cash_crops(harvest_stores)
    ul.apply_cash_crop_yield(cash_crops)
    ul.report_sold(cash_crops)
    harvest_stores = harvest_stores.sub(cash_crops, fill_value=0.0)
    harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
    ul.apply_animal_balance(animals_on_farm)
    ul.apply_electricity_use()
    ul.fertilize_fm()
    ul.report_and_wipe_fm()
    print(f'years passed: {gd.year}')
    print(f'herd size is: {sum(animals_on_farm)}\n')

    while gd.year < gd.estate_values['runtime']:
        gd.year += 1
        al.age_herd(animals_on_farm)
        ul.apply_stocking_limits(animals_on_farm)
        harvest_stores = gd.harvest_yield.copy()
        ul.apply_crop_balance()
        ul.fixate_fm(harvest_stores)
        bedding = ul.assign_bedding(harvest_stores, animals_on_farm)
        ul.report_bedding(bedding)
        harvest_stores = harvest_stores.sub(bedding, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        feed = fd.feed_animals(harvest_stores, animals_on_farm)
        ul.report_feed(feed)
        harvest_stores -= feed
        ul.apply_digestion_methane_emission(animals_on_farm)
        manure = animals_on_farm * gd.animal_data['manure_pasture_production']
        ul.apply_manure(manure)
        biomatter_available = bi.biopro_all(harvest_stores, animals_on_farm)
        biomatter_use = bi.biopro_to_use(biomatter_available)
        ul.report_digestor(biomatter_use)
        ul.extract_fm(biomatter_use)
        bi.make_biopro_products(biomatter_use)
        ul.apply_digestate()
        harvest_stores = harvest_stores.sub(biomatter_use, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        mulch = ul.select_mulch(harvest_stores, biomatter_available,
                                biomatter_use)
        ul.report_mulch(mulch)
        ul.apply_mulch(mulch)
        harvest_stores = harvest_stores.sub(mulch, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        cash_crops = ul.select_cash_crops(harvest_stores)
        ul.apply_cash_crop_yield(cash_crops)
        ul.report_sold(cash_crops)
        harvest_stores = harvest_stores.sub(cash_crops, fill_value=0.0)
        harvest_stores = harvest_stores.reindex_like(gd.harvest_yield)
        ul.apply_animal_balance(animals_on_farm)
        ul.apply_electricity_use()
        ul.fertilize_fm()
        ul.report_and_wipe_fm()
        animals_on_farm.name = f'year_{gd.year}'
        gd.herd_results.append(animals_on_farm.copy())
        print(f'years passed: {gd.year}')
        print(f'herd size is: {sum(animals_on_farm)}\n')
        # females = sum(animals_on_farm[gd.female_labs[:-1]])
        # males = sum(animals_on_farm[gd.male_labs[:-1]])
        # print(f'female per male is: {females/males}\n')

    print(f'final herd is:\n{animals_on_farm}\n')

    gd.herd_results = pd.DataFrame(gd.herd_results)
    gd.bedding_used = pd.DataFrame(gd.bedding_used)
    gd.feed_used = pd.DataFrame(gd.feed_used)
    ul.drop_empty_columns(gd.feed_used)
    gd.crops_sold = pd.DataFrame(gd.crops_sold)
    gd.digestor_used = pd.DataFrame(gd.digestor_used)
    gd.digestor_used.fillna(0, inplace=True)
    gd.mulch_used = pd.DataFrame(gd.mulch_used)
    gd.mulch_used.fillna(0, inplace=True)

    # At the end of the run output relevant results and inputs used.
    timestamp = dt.datetime.now()
    timestamp = timestamp.strftime('%Y-%m-%d_%H.%M.%S')
    output_name = f'squire_results_{timestamp}.xlsx'
    with pd.ExcelWriter(output_name) as writer:
        gd.results.to_excel(writer, sheet_name='statistics')
        gd.herd_results.to_excel(writer, sheet_name='herd')
        gd.feed_used.to_excel(writer, sheet_name='feed use(Kg)')
        gd.bedding_used.to_excel(writer, sheet_name='bedding use(Kg)')
        gd.crops_sold.to_excel(writer, sheet_name='crops sold(Kg)')
        gd.digestor_used.to_excel(writer, sheet_name='biodigestor inputs(Kg)')
        gd.mulch_used.to_excel(writer, sheet_name='mulch applied(Kg)')
        gd.estate_data_ori.to_excel(writer, sheet_name='estate')
        gd.plant_data_ori.to_excel(writer, sheet_name='crops')
        gd.animal_data_ori.to_excel(writer, sheet_name='animal')
        gd.biodigestor_data_ori.to_excel(writer, sheet_name='biodigestor')
    print('simulation done, check output file')
    os.system(f'start EXCEL.EXE {output_name}')
