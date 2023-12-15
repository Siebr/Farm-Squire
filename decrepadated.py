# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 16:41:07 2023

@author: siebr
"""

def find_best_ratio(ratio_list, list_pos, ratio_max, ratio_remaining, 
                    list_of_ratio_lists):
    copy_ratio_list=ratio_list.copy()
    if list_pos == len(copy_ratio_list) - 1:
        copy_ratio_list[list_pos] = ratio_remaining
        list_of_ratio_lists.append(copy_ratio_list)
        return
    else:
        for set_ratio in np.arange(ratio_remaining, -1 , -1):
            copy_ratio_list[list_pos] = set_ratio
            ratio_remaining = ratio_max - sum(copy_ratio_list)
            find_best_ratio(copy_ratio_list, list_pos + 1, ratio_max, 
                            ratio_remaining, list_of_ratio_lists)
    return

def find_feed_optim(feed_use_cumul, feed_needs, feed_limits, harvest_yield, 
                    feed_sources):
    feed_left = harvest_yield - feed_use_cumul
    feed_comp = mk_feed_ratio_as_available (feed_left, feed_sources)
    source_data = plant_data.loc[feed_sources]
    
    prot_yield_source = source_data['feed_protein_content']
    energy_yield_source = source_data['feed_energy_content']
    
    prot_per_comp_Kg = sum(feed_comp * prot_yield_source)
    energy_per_comp_Kg = sum(feed_comp * energy_yield_source)
    DM_per_comp_Kg = 1
    
    comp_Kg_for_prot = feed_needs['protein'] / prot_per_comp_Kg
    comp_Kg_for_energy = feed_needs['energy'] / energy_per_comp_Kg
    comp_Kg_for_DM = feed_needs['DM'] / DM_per_comp_Kg
    
    comp_Kg_needed = max(comp_Kg_for_prot, 
                          comp_Kg_for_energy, 
                          comp_Kg_for_DM)
    within_margin = check_margin_of_comp(comp_Kg_needed, feed_comp, feed_needs, 
                                  feed_limits, source_data)
    
    if within_margin :
        feed_to_use = feed_comp * comp_Kg_needed
    else:
        feed_comp = fit_feed_comp()##
        feed_to_use = feed_comp * comp_Kg_needed
    return feed_to_use

def mk_feed_ratio_as_available (harvest_stores, feed_sources):
    """
    Parameters
    ----------
    harvest_stores : pd.Series of current feed stores considered.
    feed_sources : List of feed types to consider for producing ratio.
    Returns
    -------
    feed_ratio_as_available : pd.Series of feed types depicting the ratio 
    in which they are available in the feed stores.
    """
    feeding_stores = harvest_stores.loc[feed_sources]
    feed_total = sum(feeding_stores)
    feed_ratio_as_available = feeding_stores / feed_total
    return feed_ratio_as_available

def check_margin_of_comp (comp_Kg, feed_comp, feed_needs, feed_limits, 
                          source_data):
    """
    Parameters
    ----------
    comp_Kg_needed : np.float64: amount of Kg of feed composition attempting 
    to be fed.
    feed_comp : pd.Series containing the relative ratio in which current feeds
    are being fed.
    feed_needs : pd.Series that countains the minimal nutrient needs for
    the current herd of animals.
    feed_limits : pd.Series that contains the maxium nutrient amounts the
    herd could be fed.
    source_data : pd.Dataframe containing all properties of the selected subset 
    of plant_yields.
    Returns
    -------
    bool
    True if given feed composition and amount fit within nutrient limits
    specified.
    False if not.
    """
    feed_to_use = feed_comp * comp_Kg
    prot_yield = sum(feed_to_use * source_data['feed_protein_content'])
    energy_yield = sum(feed_to_use * source_data['feed_energy_content'])
    DM_yield = sum (feed_to_use)
    if (prot_yield <= feed_limits['protein'] and 
        prot_yield >= feed_needs['protein']):
        if (energy_yield <= feed_limits['energy'] and 
            energy_yield >= feed_needs['energy']):
            if (DM_yield <= feed_limits['DM'] and 
                DM_yield >= feed_needs['DM']):
                return True
    return False

def mk_yields_from_feed(feed_used, source_data):
    label = feed_used.index[0]
    amount = feed_used.iat[0]
    prot_yield = source_data['feed_protein_content'].loc[label] * amount
    energy_yield = source_data['feed_energy_content'].loc[label] * amount
    DM_yield = amount
    
    feed_yields = {'protein' : prot_yield,
                   'energy' : energy_yield,
                   'DM' : DM_yield}
    feed_yields = pd.Series(feed_yields)
    return feed_yields

     if most_Kg_needed <= 0 :
         print('could not prevent overfeeding\n')
         break
     elif (most_Kg_needed < second_most_Kg_needed + 10 and 
         most_Kg_needed < third_most_Kg_needed + 10):
         Kg_to_feed = third_most_Kg_needed
         most_Kg_needed = third_most_Kg_needed
     elif most_Kg_needed < second_most_Kg_needed + 10 :
         Kg_to_feed = second_most_Kg_needed - third_most_Kg_needed
         most_Kg_needed = second_most_Kg_needed
     else: 
         Kg_to_feed = most_Kg_needed - second_most_Kg_needed
         
         return
 

def find_worst_prot_yielder(source_data):
    prot_values = source_data['feed_protein_content']
    best = source_data.index.where(prot_values == min(prot_values))
    if len(best) > 1:
        best = best.drop(None)
    best = best[0]
    return best

def find_worst_energy_yielder(source_data):
    energy_values = source_data['feed_energy_content']
    best = source_data.index.where( energy_values == min(energy_values))
    if len(best) > 1:
        best = best.drop(None)
    best = best [0]
    return best


def reduce_animal(animals_on_farm):
    """
    Do description.

    Parameters
    ----------
    animals_on_farm : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    categories = " ".join(animals_on_farm.index)
    castrated_tups = re.findall(r'[\^ ](male_castrated_(\d+)_year)',\
                                categories)
    male_tups = re.findall(r'[\^ ](male_(\d+)_year)', categories)
    female_tups = re.findall(r'[\^ ](female_(\d+)_year)', categories)
    castrated_labs = []
    castrated_ages = []
    male_labs = []
    male_ages = []
    female_labs = []
    female_ages = []
    castrated_tups.sort(reverse= True)
    male_tups.sort(reverse= True)
    female_tups.sort(reverse= True)
    for tup in castrated_tups:
        castrated_labs.append(tup[0])
        castrated_ages.append(tup[1])
    for tub in male_tubs:
        male_labs.append(tup[0])
        male_ages.append(tup[1])
    for tub in female_tups:
        female_labs.append(tup[0])
        female_ages.append(tup[1])
    print(castrated_labs)
    print(castrated_ages)
        
    
    return
    for label in castrated_labs:
        if animals_on_farm[label] > 0:
            animals_on_farm[label] -= 1
            # do slaugther yields
            return
    label = "male_0_year"
    if animals_on_farm[label] > 1:
        animals_on_farm[label] -= 1
        # do slaughter
        return
    ratio = gd.estate_values['male_ratio'] / gd.estate_values['female_ratio']
    if sum(animals_on_farm[male_labs]) >0:
        pass
    for age in males:
        print(f"male_{age}_year")
    for age in females:
        print(f"female_{age}_year")
    return

def find_feed_cumul(feed_needs, feed_limits, harvest_stores, max_groups,
                    try_fraction):
    """
    Find feed up to try% of feed limit without consideration for nutrient need.

    Parameters
    ----------
    feed_needs : pd.Series
        Countains the minimal nutrient needs for the current herd of animals.
    feed_limits : pd.Series
        Contains the maxium nutrient amounts the herd could be fed.
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    max_groups : int
        specifies the priority ranking up to which certain crops will be
        considered for feed purposes.
    try_fraction : float
        fraction of feed needs attempted to be fed without regards of nutrient
        requirement.

    Returns
    -------
    feed_use : pd.Series
        Contains the kg amount determined for feed for each crop.
    feed_needs : pd.Series
        Contains the minimal nutrient need for the current herd of animals
        after deducting that being generated by feed_use.
    feed_limits : pd.Series
        Contains the maxium nutrient amounts the herd could be fed after
        deducting that being genereated by feed_use.
    """
    feed_needs_cumul = feed_needs.copy() * 0
    feed_limits_cumul = feed_limits.copy() * try_fraction
    # retain 1 - try fraction as room for optimization
    group = 1
    feed_use = harvest_stores.copy()
    feed_use[:] = 0
    while True:
        feeding_group = mk_feeds_to_use(group, harvest_stores)
        source_data = gd.plant_data.loc[feeding_group]
        feed = harvest_stores[feeding_group]
        if check_margin(feed, feed_needs_cumul, feed_limits_cumul,
                        source_data):
            if group == max_groups:
                break
            group += 1
        else:
            if group == 1:
                return (feed_use, feed_needs, feed_limits)
            group -= 1
            feeding_group = mk_feeds_to_use(group, harvest_stores)
            break
    feed_use[feeding_group] = harvest_stores[feeding_group]
    feed_satisfied = mk_yields_from_groups(group)
    feed_needs = feed_needs - feed_satisfied
    feed_limits = feed_limits - feed_satisfied
    return (feed_use, feed_needs, feed_limits)

def feed_animals(harvest_stores, animals_on_farm):
    """
    Feed animals and remove that feed from harvest stores.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    """
    feed_needs = mk_feed_needs(animals_on_farm)
    feeding_groups_used = determine_feeding_groups(feed_needs)
    while feeding_groups_used == 0:
        sl.reduce_animal(animals_on_farm)
        feed_needs = mk_feed_needs(animals_on_farm)
        feeding_groups_used = determine_feeding_groups(feed_needs)
    feed_limits = mk_feed_limits(animals_on_farm)

    feed_use = harvest_stores.copy()
    feed_use[:] = 0
    feed_use_part = harvest_stores.copy()
    feed_use_part[:] = 0
    feed_use_optimized = harvest_stores.copy()
    feed_use_optimized[:] = 0

    while sum(feed_use_optimized) == 0 and\
        feeding_groups_used <= max(gd.plant_data['feeding_priority']):
        feeding_groups_part = feeding_groups_used - 1
        lower_part = 1 - gd.estate_values['optimization_modifier']
        while lower_part >= 0 and sum(feed_use_optimized) == 0 :
            harvest_stores_temp = harvest_stores.copy()
            feed_limits_temp = feed_limits.copy()
            feed_needs_part = feed_needs * lower_part
            feed_use_part, feed_needs_part, feed_limits_temp =\
                find_feed_optim(harvest_stores_temp, feed_needs_part,
                                feed_limits_temp, feeding_groups_part)
            feed_needs_temp = feed_needs_part + feed_needs * (1 - lower_part)
            feed_use_optimized, feed_needs_temp, feed_limits_temp =\
                find_feed_optim(harvest_stores_temp, feed_needs_temp,
                                feed_limits_temp, feeding_groups_used)
            lower_part -= gd.estate_values['optimization_modifier']
            print(lower_part)
        feeding_groups_used += 1
    
    if sum(feed_use_optimized) == 0:
        ### instead reduce animal till within feed limit?
        print('could not meet diet restraints')
    feed_use = feed_use_part + feed_use_optimized
    harvest_stores -= feed_use
    return harvest_stores 