"""
Author: Siebrant Hendriks.

Supplementary script for uncategorized functions
"""
import pandas as pd
import global_data as gd
import animal_lifecycle_functions as al


def assign_bedding(harvest_stores, animals_on_farm):
    """
    Determine how much bedding the herd needs.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    bedding_used : pd.Series
        Contains all crops suitable for bedding, and in which amount they are
        used thusly.

    """
    bedding_crops = harvest_stores.where(gd.plant_data['bedding_use'] == True)
    bedding_crops = bedding_crops.where(bedding_crops > 0)
    bedding_crops.dropna(inplace=True)
    bedding_crops.sort_values(ascending=False, inplace=True)
    bedding_per_head = gd.estate_values['bedding_required']
    bedding_needed = sum(animals_on_farm) * bedding_per_head
    bedding_used = pd.Series(0.0, index=bedding_crops.index)
    for label, amount in bedding_crops.items():
        if amount > bedding_needed:
            amount = bedding_needed
        bedding_used[label] += amount
        bedding_crops[label] -= amount
        bedding_needed -= amount
        if bedding_needed <= 0:
            break
    if bedding_needed > 0:
        al.reduce_animal(animals_on_farm)
        bedding_used = assign_bedding(harvest_stores, animals_on_farm)
    return bedding_used


def apply_stocking_limits(animals_on_farm):
    """
    Reduce the amount of animals on farm based on pasture space available.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    None.

    """
    herd_size = sum(animals_on_farm * gd.animal_data['livestock_units'])
    can_support = gd.livestock_units_max
    while herd_size > can_support:
        al.reduce_animal(animals_on_farm)
        herd_size = sum(animals_on_farm * gd.animal_data['livestock_units'])
