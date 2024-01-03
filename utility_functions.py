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
    None;
    Passed variable is altered in place.
    
    """
    herd_size = sum(animals_on_farm * gd.animal_data['livestock_units'])
    can_support = gd.livestock_units_max
    while herd_size > can_support:
        al.reduce_animal(animals_on_farm)
        herd_size = sum(animals_on_farm * gd.animal_data['livestock_units'])


def fixate_fm(harvest_stores):
    """
    Apply the fixation of fertile molecules by crops to the farmland.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    None;
    Extratedted fertile molecules get added to global variables.
    
    """
    phosphorus = sum(harvest_stores * gd.plant_data['P_fixation'])
    nitrogen = sum(harvest_stores * gd.plant_data['N_fixation'])
    gd.fertile_molecules['phosphorus'] += phosphorus
    gd.fertile_molecules['nitrogen'] += nitrogen


def extract_fm(biopro_use):
    """
    Extract fertile molecules from the matter send to the bioprocessor.

    Parameters
    ----------
    biopro_use : pd.Series
        Contains all matter types used by the bioprocessor, and the Kg amounts
        in which they are being used for the bioprocessor.

    Returns
    -------
    None;
    Extratedted fertile molecules get added to global variables.
    
    """
    for label, amount in biopro_use.items():
        if label in ['chicken_manure', 'horse_manure', 'deep_litter']:
            gd.fertile_molecules['phosphorus'] += amount *\
                gd.estate_values[f'{label}_P_content']
            gd.fertile_molecules['nitrogen'] += amount * 0.52 *\
                gd.estate_values[f'{label}_N_content']
        else:
            gd.fertile_molecules['phosphorus'] += amount *\
                gd.plant_data['P_content'].loc[label]
            gd.fertile_molecules['nitrogen'] += amount * 0.52 *\
                gd.plant_data['N_content'].loc[label]



def fertilize_fm():
    """
    Reduce nitrogen and phosphorus stores by fertilizing farmland.

    Returns
    -------
    None;
    Global data gets altered in place.
    
    """
    gd.fertile_molecules['phosphorus'] -= gd.p_use
    gd.fertile_molecules['nitrogen'] -= gd.n_use
    
    
def report_and_wipe_fm():
    """
    Set nitrogen & phosphorus balance in yearly report, and wipe for new year.

    Returns
    -------
    None;
    Global data gets altered in place
    
    """
    gd.results['phosphorus_balance'].loc[f'year_{gd.year}'] =\
        gd.fertile_molecules['phosphorus']
    gd.fertile_molecules['phosphorus'] = 0.0
    gd.results['nitrogen_balance'].loc[f'year_{gd.year}'] =\
        gd.fertile_molecules['nitrogen']
    gd.fertile_molecules['nitrogen'] = 0.0


def select_cash_crops(harvest_stores):
    cash_crops = harvest_stores.where(gd.plant_data['sale_use'] == True)
    cash_crops = harvest_stores.where(cash_crops > 0)
    cash_crops.dropna(inplace=True)
    return cash_crops


def apply_cash_crop_yield(cash_crops):
    for label, amount in cash_crops.items():
        revenue = gd.plant_data['sale_value'].loc[label] * amount
        Kcal = gd.plant_data['food_energy_content'].loc[label] * amount
        fat = gd.plant_data['food_fat_content'].loc[label] * amount
        prot = gd.plant_data['food_protein_content'].loc[label] * amount
        gd.results['revenue_balance_crops'].loc[f'year_{gd.year}'] += revenue
        gd.results['food_energy_produced'].loc[f'year_{gd.year}'] += Kcal
        gd.results['food_fat_produced'].loc[f'year_{gd.year}'] += fat
        gd.results['food_protein_produced'].loc[f'year_{gd.year}'] += prot
    return