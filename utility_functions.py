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
    # If not enough bedding available, reduce herd and try again.
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
    """
    Select all crops that are to be sold out of harvest stores.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    cash_crops : pd.Series
        Contains all crops designated to be sold.

    """
    cash_crops = harvest_stores.where(gd.plant_data['sale_use'] == True)
    cash_crops = cash_crops.where(cash_crops > 0)
    cash_crops.dropna(inplace=True)
    return cash_crops


def apply_cash_crop_yield(cash_crops):
    """
    Apply sale results of all cash crops.

    Parameters
    ----------
    cash_crops : pd.Series
        Contains all crops designated to be sold.

    Returns
    -------
    None;
    All sale results get added to global variables.

    """
    for label, amount in cash_crops.items():
        revenue = gd.plant_data['sale_value'].loc[label] * amount
        Kcal = gd.plant_data['food_energy_content'].loc[label] * amount
        fat = gd.plant_data['food_fat_content'].loc[label] * amount
        prot = gd.plant_data['food_protein_content'].loc[label] * amount
        gd.results['revenue_balance_crops'].loc[f'year_{gd.year}'] += revenue
        gd.results['food_energy_produced'].loc[f'year_{gd.year}'] += Kcal
        gd.results['food_fat_produced'].loc[f'year_{gd.year}'] += fat
        gd.results['food_protein_produced'].loc[f'year_{gd.year}'] += prot


def apply_crop_balance():
    """
    Apply flat yearly operation costs/profits of crops.

    Returns
    -------
    None;
    Operation costs/profits get added to golbal variables.
    
    """
    gd.results['revenue_balance_crops'].loc[f'year_{gd.year}'] +=\
        gd.crop_balance

    
def apply_digestion_methane_emission(animals_on_farm):
    """
    Apply methan emissions produced by digestion of herd.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    None;
    Emissions get added to global variables.

    """
    gd.results['digestion_methane_emissions'].loc[f'year_{gd.year}'] =\
        sum(animals_on_farm * gd.animal_data['digestion_methane_emission'])


def apply_manure(manure):
    """
    Apply nitrogen and phosphorus yield from manure.

    Parameters
    ----------
    manure : pd.Series
        Kg amount of manure prduced for each animal type on farm.

    Returns
    -------
    None;
    Nitrogen and phosphorus yields get added to golbal variables.
    
    """
    for label, amount in manure.items():
        nitrogen = gd.animal_data['manure_nitrogen_content'].loc[label] *\
            amount * 0.63
        phosphorus = gd.animal_data['manure_phosphorus_content'].loc[label] *\
            amount
        methane = gd.animal_data['manure_methane_content'].loc[label] *\
            amount
        gd.results['manure_methane_emissions'].loc[f'year_{gd.year}'] +=\
            methane
        gd.fertile_molecules['nitrogen'] += nitrogen
        gd.fertile_molecules['phosphorus'] += phosphorus


def select_mulch(harvest_stores, biomatter_available, biomatter_use):
    mulch = harvest_stores.where(gd.plant_data['mulch_use'] == True)
    mulch = mulch.where(mulch > 0)
    mulch.dropna(inplace=True)
    deep_litter = biomatter_available['deep_litter'] -\
        biomatter_use['deep_litter']
    deep_litter = {'deep_litter': deep_litter}
    deep_litter = pd.Series(deep_litter)
    mulch = pd.concat([mulch, deep_litter])
    return mulch


def apply_mulch(mulch):
    for label, amount in mulch.items():
        if label == 'deep_litter':
            nitrogen = gd.estate_values[f'{label}_N_content'] * 0.7 * amount
            phosphorus = gd.estate_values[f'{label}_P_content'] * amount
            gd.fertile_molecules['nitrogen'] += nitrogen
            gd.fertile_molecules['phosphorus'] += phosphorus
        else:
            nitrogen = gd.plant_data['N_content'].loc[label] * 0.8 * amount
            phosphorus = gd.plant_data['P_content'].loc[label] * amount
            gd.fertile_molecules['nitrogen'] += nitrogen
            gd.fertile_molecules['phosphorus'] += phosphorus
            

def apply_animal_balance(animals_on_farm):
    balance = sum(animals_on_farm * gd.animal_data['subsidies_gained'])
    labour = sum(animals_on_farm * gd.animal_data['general_labour_costs'])
    labour_cost = labour * gd.estate_values['casual_labour_cost']
    balance -= labour_cost
    livestock_units = sum(animals_on_farm * gd.animal_data['livestock_units'])
    maintenance_cost = gd.estate_values['animal_maintenance'] * livestock_units
    balance -= maintenance_cost
    gd.results['revenue_balance_animal'].loc[f'year_{gd.year}'] += balance
    electricity_use = sum(animals_on_farm * gd.animal_data['electricity_use'])
    gd.results['electricity_balance'].loc[f'year_{gd.year}'] -= electricity_use


def apply_electricity_use():
    gd.results['electricity_balance'].loc[f'year_{gd.year}'] -=\
        gd.estate_values['general_electricity_consumption']
    if gd.brewery == True:
        gd.results['electricity_balance'].loc[f'year_{gd.year}'] -=\
            gd.estate_values['brewery_electricity_requirement']


def apply_digestate():
    digestate = gd.results['digestate_produced'].loc[f'year_{gd.year}']
    cost = gd.estate_values['digestate_application_cost'] * digestate
    gd.results['revenue_balance_crops'].loc[f'year_{gd.year}'] -= cost