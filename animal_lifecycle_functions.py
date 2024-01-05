"""
Author: Siebrant Hendriks.

Supplementary script for slaughtering animals
"""
from random import random
from random import seed
import numpy as np
import global_data as gd
seed('squire')  # this hopefully will give consistent results on retries


def apply_slaughter_yield(animal_label):
    """
    Apply (add) slaughter yields (revenue/nutrients) of slaughtered animal.

    Parameters
    ----------
    animal_label : str
        Name of the group/type the animal being slaughtered belongs to.

    Returns
    -------
    None;
    Yields get added to global variables.

    """
    meat_yield = gd.animal_data['slaughter_meat_yield'].loc[animal_label]
    meat_value = gd.animal_data['meat_sale_value'].loc[animal_label]
    diet_engergy = gd.estate_values['meat_diet_energy_content']
    diet_protein = gd.estate_values['meat_diet_protein_content']
    diet_fat = gd.estate_values['meat_diet_fat_content']
    gd.results['revenue_balance_animal'].loc[f'year_{gd.year}'] +=\
        meat_yield * meat_value
    gd.results['food_energy_produced'].loc[f'year_{gd.year}'] += meat_yield *\
        diet_engergy
    gd.results['food_protein_produced'].loc[f'year_{gd.year}'] += meat_yield *\
        diet_protein
    gd.results['food_fat_produced'].loc[f'year_{gd.year}'] += meat_yield *\
        diet_fat


def age_herd(animals_on_farm):
    """
    Age the herd by one year; slaughter expired and introduce newborns.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    None;
    Passed variable gets altered in place.

    """
    newborn_male = 0
    newborn_female = 0
    for pos, label in enumerate(gd.castrated_labs):
        amount = animals_on_farm[label]
        if pos == 0:
            for _ in range(amount):
                apply_slaughter_yield(label)
        else:
            label = gd.castrated_labs[pos - 1]
            animals_on_farm[label] = amount

    for pos, label in enumerate(gd.female_labs):
        fert = gd.animal_data['fertility_rate'].loc[label]
        decider_1 = random()
        decider_2 = random()
        non_whole = animals_on_farm[label] * fert
        whole = np.floor(non_whole)
        rest = non_whole - whole
        if decider_1 < rest:
            succes = whole + 1
        elif decider_1 >= rest:
            succes = whole
        if decider_2 < 0.5:
            newborn_male += np.ceil(succes * 0.5)
            newborn_female += np.floor(succes * 0.5)
        elif decider_2 >= 0.5:
            newborn_male += np.floor(succes * 0.5)
            newborn_female += np.ceil(succes * 0.5)
        if fert == 0:
            succes = animals_on_farm[label]
        fail = animals_on_farm[label] - succes
        if pos == 0:
            for _ in range(animals_on_farm[label]):
                apply_slaughter_yield(label)
        else:
            for _ in range(int(fail)):
                apply_slaughter_yield(label)
            label = gd.female_labs[pos - 1]
            animals_on_farm[label] = int(succes)

    for pos, label in enumerate(gd.male_labs[:-1]):
        amount = animals_on_farm[label]
        if pos == 0:
            for _ in range(amount):
                apply_slaughter_yield(label)
        else:
            label = gd.male_labs[pos - 1]
            animals_on_farm[label] = amount

    male_ratio = gd.estate_values['female_ratio'] /\
        gd.estate_values['male_ratio']

    male_limit = sum(animals_on_farm[gd.female_labs[:-1]]) / male_ratio
    males_present = sum(animals_on_farm[gd.male_labs[:-1]])
    while males_present > male_limit:
        for label in gd.male_labs[:-1]:
            if animals_on_farm[label] > 0:
                animals_on_farm[label] -= 1
                apply_slaughter_yield(label)
        males_present = sum(animals_on_farm[gd.male_labs[:-1]])
    males_to_add = 0
    if males_present < male_limit:
        males_to_add = np.ceil(male_limit) - males_present
    if males_to_add > animals_on_farm['male_0_year']:
        males_to_add = animals_on_farm['male_0_year']
    males_to_castrate = animals_on_farm['male_0_year'] - males_to_add
    animals_on_farm['male_1_year'] = int(males_to_add)
    animals_on_farm['male_castrated_1_year'] = int(males_to_castrate)
    animals_on_farm['male_0_year'] = int(newborn_male)
    animals_on_farm['female_0_year'] = int(newborn_female)


def reduce_animal(animals_on_farm):
    """
    Remove the least wanted animal from the farm.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    None;
    Passed variables gets altered in place.

    """
    all_males = animals_on_farm[gd.male_labs]
    fertile_males = gd.animal_data['fertility_rate'].loc[gd.male_labs] > 0
    fertile_males = all_males[fertile_males]
    fertile_male_amount = sum(fertile_males)

    all_females = animals_on_farm[gd.female_labs]
    fertile_females = gd.animal_data['fertility_rate'].loc[gd.female_labs] > 0
    fertile_females = all_females[fertile_females]
    fertility_rates = gd.animal_data['fertility_rate']\
        .loc[fertile_females.index]
    fertile_female_amount = sum(fertile_females * fertility_rates)

    newborn_amount = sum(animals_on_farm[['male_0_year', 'female_0_year']])

    for label in gd.castrated_labs:
        if animals_on_farm[label] > 0:
            animals_on_farm[label] -= 1
            apply_slaughter_yield(label)
            return

    ratio_want = gd.estate_values['male_ratio'] /\
        gd.estate_values['female_ratio']
    ratio_current = fertile_male_amount / fertile_female_amount
    if ratio_current > ratio_want:
        for label in fertile_males.index:
            if animals_on_farm[label] > 0:
                animals_on_farm[label] -= 1
                apply_slaughter_yield(label)
                return

    ratio_want = gd.estate_values['female_ratio'] /\
        gd.estate_values['newborn_ratio']
    ratio_current = fertile_female_amount / newborn_amount
    if ratio_current > ratio_want:
        for label in fertile_females.index:
            if animals_on_farm[label] > 0:
                animals_on_farm[label] -= 1
                apply_slaughter_yield(label)
                return
            
    if animals_on_farm['female_0_year'] > animals_on_farm['male_0_year']:
        label = 'female_0_year'
        if animals_on_farm[label] > 0:
            animals_on_farm[label] -= 1
            apply_slaughter_yield(label)
            return
    
    if animals_on_farm['male_0_year'] >= animals_on_farm['female_0_year']:
        ratio_current = sum(all_males[1:]) / fertile_female_amount
        ratio_want = gd.estate_values['male_ratio'] /\
            gd.estate_values['female_ratio']
        label = 'male_0_year'
        if ratio_current > ratio_want and animals_on_farm[label] > 0:
            animals_on_farm[label] -= 1
            apply_slaughter_yield(label)
            return
    
    print('cannot reduce herd further')
    return
