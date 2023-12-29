"""
Author: Siebrant Hendriks.

Supplementary script for bioprocessor use
"""
import pandas as pd
import global_data as gd


def biopro_no_mulch(harvest_stores):
    """
    Get crops from harvest_stores that can "only" be used for bioprocessor.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    bio_crops : pd.Series
        Contains crops suitable for bioprocessor and their stored Kg amount.

    """
    bio_crops = harvest_stores.where(gd.plant_data['bioprocessor_use'] == True)
    bio_crops = bio_crops.where(gd.plant_data['mulch_use'] == False)
    bio_crops = bio_crops.where(bio_crops > 0)
    bio_crops.dropna(inplace=True)
    return bio_crops


def biopro_with_mulch(harvest_stores):
    """
    Get crops that can be used either for mulch or bioprocessor.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    bio_crops : pd.Series
        Contains crops suitable for bioprocessor and their stored Kg amount.

    """
    bio_crops = harvest_stores.where(gd.plant_data['bioprocessor_use'] == True)
    bio_crops = bio_crops.where(gd.plant_data['mulch_use'] == True)
    bio_crops = bio_crops.where(bio_crops > 0)
    bio_crops.dropna(inplace=True)
    return bio_crops


def get_deep_litter(animals_on_farm):
    """
    Calculate the Kg amount of deep litter produced by the animals on the farm.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    deep_litter : float
        Kg amount of deep litter produced.

    """
    deep_litter = sum(animals_on_farm *
                      gd.animal_data['deep_litter_production'])
    return deep_litter


def biopro_animal(animals_on_farm):
    """
    Select animal related matter suitable for the bioprocessor.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    bio_anim : pd.Series
        Contains matter types suitable for bioprocessor and their Kg amount.

    """
    deep_litter = get_deep_litter(animals_on_farm)
    chicken_manure = gd.estate_values['import_chicken_manure']
    horse_manure = gd.estate_values['import_horse_manure']
    bio_anim = {'chicken_manure': chicken_manure, 'horse_manure': horse_manure,
                'deep_litter': deep_litter}
    bio_anim = pd.Series(bio_anim)
    return bio_anim


def biopro_all(harvest_stores, animals_on_farm):
    """
    Get all matter suitable for bioprocessor in order of preferred use.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    biopro_available : pd.Series
        Contains matter types suitable for bioprocessor and their Kg amount.
        Series is ordered to have preferred matter appear first.

    """
    biopro_available = biopro_animal(animals_on_farm)
    biopro_available = pd.concat([biopro_available,
                                  biopro_no_mulch(harvest_stores)])
    biopro_available = pd.concat([biopro_available,
                                  biopro_with_mulch(harvest_stores)])
    return biopro_available


def biopro_to_use(bio_available):
    """
    Determine how much matter will be used by the bioprocessor this year.

    Parameters
    ----------
    bio_input : pd.Series
        Contains matter types suitable for bioprocessor and their Kg amount.
        Series is ordered to have preferred matter appear first.

    Returns
    -------
    biopro_to_use : pd.Series
        Contains matter types suitable for bioprocessor and their Kg amount
        that will be used by the bioprocessor.

    """
    digest_max = gd.estate_values['maximum_digestate_spreadable']
    biopro_to_use = pd.Series(0.0, index=bio_available.index)
    for label, amount in bio_available.items():
        digest_yield = amount * gd.biodigestor_data['digestate'].loc[label]
        if digest_yield > digest_max:
            amount = digest_max / gd.biodigestor_data['digestate'].loc[label]
        biopro_to_use[label] = amount
        digest_max -= amount * gd.biodigestor_data['digestate'].loc[label]
        if digest_max <= 0:
            break
    return biopro_to_use


def make_biopro_products(bio_input):
    """
    

    Parameters
    ----------
    bio_input : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    for label, amount in bio_input.items():
        digestate = gd.biodigestor_data['digestate'].loc[label] * amount
        electricity = gd.biodigestor_data['electricity'].loc[label] * amount
        methane = gd.biodigestor_data['biomethane'].loc[label] * amount
        gd.results['digestate_produced'].loc[f'year_{gd.year}'] += digestate
        gd.results['electricity_balance'].loc[f'year_{gd.year}'] += electricity
        gd.results['biomethane_produced'].loc[f'year_{gd.year}'] += methane