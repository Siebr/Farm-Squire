"""
Author: Siebrant Hendriks.

Supplementary script for feeding animals
"""
import re
import pandas as pd
import numpy as np
import global_data as gd
import animal_lifecycle_functions as al


class NutrientData:
    """
    Nutrient data contains most variables relevant to finding optimal feed.

    Attribues:
    ----------
    p_lab : str
        Name of best available protein yielding feed source.
    e_lab : str
        Name of best available energy yielding feed source.
    dm_lab : str
        Name of best available dry matter yielding feed source.
    p_yld : float
        The kg amount of protein 1 kg of p_lab would yield.
    e_yld : float
        The MJ amount of energy 1 kg of e_lab would yield.
    p_kg : float
        The persumed amount of kg feed needed to meet protein demands.
    e_kg : float
        The persumed amount of kg feed needed to meet energy demands.
    dm_kg : float
        The persumed amount of kg feed needed to meet dry matter demands.
    first : float
        The most kg feed needed to satisfy one of the nutrient requirements.
    second : float
        The second most kg feed needed to satisfy one of the nutrient
        requirements.
    third : float
        the third most kg feed needed to satisfy one of the nutrient
        requirements.
    kg_tf : float
        the eventual amount of kg feed that wiil be fed at this stage
        in the feeding process.
    """

    def __init__(self, source_data, feed_needs_remain, harvest_stores):
        self.assign_p_lab(source_data)
        self.assign_e_lab(source_data)
        self.assign_p_yld(self.p_lab, source_data)
        self.assign_e_yld(self.e_lab, source_data)
        self.assign_p_kg(self.p_lab, self.p_yld, source_data,
                         feed_needs_remain, harvest_stores)
        self.assign_e_kg(self.e_lab, self.e_yld, source_data,
                         feed_needs_remain, harvest_stores)
        self.assign_dm_lab(source_data, self.p_kg, self.e_kg)
        self.assign_dm_kg(feed_needs_remain)
        self.rank_kg(self.p_kg, self.e_kg, self.dm_kg)
        self.assign_tf(self.first, self.second, self.third)

    def assign_p_lab(self, source_data):
        """
        Assign protein label based on new source data.

        Parameters
        ----------
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.

        Returns
        -------
        None.
        """
        self.p_lab = find_best_prot_yielder(source_data)

    def assign_p_yld(self, p_lab, source_data):
        """
        Assign protein yield based on new source data.

        Parameters
        ----------
        p_lab : str
            Name of best available protein yielding feed source.
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.

        Returns
        -------
        None.
        """
        self.p_yld = source_data['feed_protein_content'].loc[p_lab]

    def assign_p_kg(self, p_lab, p_yld, source_data, feed_needs_remain,
                    harvest_stores):
        """
        Assign kg of feed needed based on protein needs.

        Parameters
        ----------
        p_lab : str
            Name of best available protein yielding feed source.
        p_yld : float
            The kg amount of protein 1 kg of p_lab would yield.
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.
        feed_needs_remain : pd.Series
            Contains the remaning nutrient needs
            (protein, energy and dry matter) of the herd.
        harvest_stores : pd.Series
            Contains all harvested crops and their stored amounts.

        Returns
        -------
        None.
        """
        self.p_kg = find_kg_need_for_prot(p_lab, p_yld, source_data,
                                          feed_needs_remain,
                                          harvest_stores)

    def assign_e_lab(self, source_data):
        """
        Assing energy label based on new source data.

        Parameters
        ----------
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.

        Returns
        -------
        None.
        """
        self.e_lab = find_best_energy_yielder(source_data)

    def assign_e_yld(self, e_lab, source_data):
        """
        Assign energy yield based on source data.

        Parameters
        ----------
        e_lab : str
            Name of best available energy yielding feed source.
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.

        Returns
        -------
        None.
        """
        self.e_yld = source_data['feed_energy_content'].loc[e_lab]

    def assign_e_kg(self, e_lab, e_yld, source_data, feed_needs_remain,
                    harvest_stores):
        """
        Assign kg of feed needed based on energy needs.

        Parameters
        ----------
        e_lab : str
            Name of best available energy yielding feed source.
        e_yld : float
            The MJ amount of energy 1 kg of e_lab would yield.
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.
        feed_needs_remain : pd.Series
            Contains the remaning nutrient needs
            (protein, energy and dry matter) of the herd.
        harvest_stores : pd.Series
            Contains all harvested crops and their stored amounts.

        Returns
        -------
        None.
        """
        self.e_kg = find_kg_need_for_energy(e_lab, e_yld, source_data,
                                            feed_needs_remain,
                                            harvest_stores)

    def assign_dm_lab(self, source_data, p_kg, e_kg):
        """
        Assign dry matter label based on new source data and nutrient needs.

        Parameters
        ----------
        source_data : pd.Dataframe
            Data frame containing all attributes relevant to selection of feed.
        p_kg : float
            The persumed amount of kg feed needed to meet protein demands.
        e_kg : float
            The persumed amount of kg feed needed to meet energy demands.

        Returns
        -------
        None.
        """
        self.dm_lab = find_best_dm_yielder(source_data, p_kg, e_kg)

    def assign_dm_kg(self, feed_needs_remain):
        """
        Assign kg of feed needed based on dry matter needs.

        Parameters
        ----------
        feed_needs_remain : pd.Series
            Contains the remaning nutrient needs
            (protein, energy and dry matter) of the herd.

        Returns
        -------
        None.
        """
        self.dm_kg = feed_needs_remain['dm']
        if self.dm_kg < 0:
            self.dm_kg = float(0)

    def rank_kg(self, p_kg, e_kg, dm_kg):
        """
        Rank the kg needs of each nutrient in descending order.

        Parameters
        ----------
        p_kg : float
            The persumed amount of kg feed needed to meet protein demands.
        e_kg : float
            The persumed amount of kg feed needed to meet energy demands.
        dm_kg : float
            The persumed amount of kg feed needed to meet dry matter demands.

        Returns
        -------
        None.
        """
        kg_list = [p_kg, e_kg, dm_kg]
        kg_list.sort(reverse=True)
        self.first = kg_list[0]
        self.second = kg_list[1]
        self.third = kg_list[2]

    def assign_tf(self, first, second, third):
        """
        Assing the amount of kg to feed at this stage of the feeding process.

        Parameters
        ----------
        first : float
            The most kg feed needed to satisfy one of the nutrient
            requirements.
        second : float
            The second most kg feed needed to satisfy one of the nutrient
            requirements.
        third : float
            the third most kg feed needed to satisfy one of the nutrient
            requirements.

        Returns
        -------
        None.
        """
        if first < second + 100:
            if second == self.dm_kg:
                self.kg_tf = first - third
            else:
                self.kg_tf = float(100)
        else:
            self.kg_tf = first - second


def find_best_prot_yielder(source_data):
    """
    Find crop that yields the most protein per Kg present in source data.

    Parameters
    ----------
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.

    Returns
    -------
    best : string
        The name of the available crop yielding the most protein.
    """
    protein_rank = source_data['feed_protein_content']
#   alternate selection criterea below
#   protein_rank /= source_data['feed_energy_content']
    best_rank = protein_rank.nlargest(n=1)
    best = best_rank.index[0]
    return best


def find_best_energy_yielder(source_data):
    """
    Find crop that yields the most energy per Kg present in source data.

    Parameters
    ----------
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.

    Returns
    -------
    best : string
        The name of the available crop yielding the most energy.
    """
    energy_rank = source_data['feed_energy_content']
#   alternate selection criterea below
#   energy_rank /= source_data['feed_protein_content']
    best_rank = energy_rank.nlargest(n=1)
    best = best_rank.index[0]
    return best


def find_best_dm_yielder(source_data, kg_need_for_prot, kg_need_for_energy):
    """
    Find crop that can best be used to satisfy dry matter requirement.

    Parameters
    ----------
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.
    kg_need_for_prot : float
        Persumed amount of kg feed needed to satisfy protein needs.
    kg_need_for_energy : float
        Persumed amount of kg feed needed to satisfy energy needs.

    Returns
    -------
    best : string
        The name of the available harvest product best fit to satisfy
        dry matter requirement in the current situation.
    """
    energy_rank = source_data['feed_energy_content'].rank()
    protein_rank = source_data['feed_protein_content'].rank()
    if kg_need_for_prot >= kg_need_for_energy:
        use_rank = energy_rank
    elif kg_need_for_energy > kg_need_for_prot:
        use_rank = protein_rank
    best = use_rank
    best = best.nsmallest(n=1)
    best = best.index[0]
    return best


def find_kg_need_for_prot(p_lab, p_yld, source_data, feed_needs_remain,
                          harvest_stores):
    """
    Determine persumed Kg amound of feed needed to satisfy protein need.

    Parameters
    ----------
    p_lab : str
        Name of best protein yielding crop.
    p_yld : TYPE
        Kg amount of protein yield per Kg of crop fed.
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.
    feed_needs : pd.Series
        Countains the minimal nutrient needs for the current herd of animals at
        this stage in the feeding algorithm.
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    kg_need_for_prot : float
        The persumed Kg amount of feed needed to satisfy protein requirement.
    """
    prot_yield = 0.0
    kg_needed = 0.0
    fail = False  # might want to figure out better fail safe later
    while prot_yield < feed_needs_remain['protein']:
        prot_yield += harvest_stores[p_lab] * p_yld
        kg_needed += harvest_stores[p_lab]
        if prot_yield < feed_needs_remain['protein']:
            source_data_popped = source_data.drop(p_lab)
            if 0 >= len(source_data_popped):
                fail = True
                break
            p_lab = find_best_prot_yielder(source_data_popped)
            p_yld = source_data['feed_protein_content'].loc[p_lab]
    surplus = prot_yield - feed_needs_remain['protein']
    kg_needed -= surplus / p_yld
    if fail:
        kg_needed = 0
    return kg_needed


def find_kg_need_for_energy(e_lab, e_yld, source_data, feed_needs_remain,
                            harvest_stores):
    """
    Determine the persumed Kg amount of feed needed to satsify energy need.

    Parameters
    ----------
    e_lab : str
        Name of best energy yielding crop
    e_yld : float
        MJ amount of energy yield per Kg of crop fed.
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.
    feed_needs : pd.Series
        Countains the minimal nutrient needs for the current herd of animals at
        this stage in the feeding algorithm.
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    kg_need_for_energy : float
        The persumed Kg amount of feed needed to satsify energy need.
    """
    energy_yield = 0.0
    kg_needed = 0.0
    fail = False  # might want to figure out better fail safe later
    while energy_yield < feed_needs_remain['energy']:
        energy_yield += harvest_stores[e_lab] * e_yld
        kg_needed += harvest_stores[e_lab]
        if energy_yield < feed_needs_remain['energy']:
            source_data_popped = source_data.drop(e_lab)
            if 0 >= len(source_data_popped):
                fail = True
                break
            e_lab = find_best_energy_yielder(source_data_popped)
            e_yld = source_data['feed_energy_content'].loc[e_lab]
    surplus = energy_yield - feed_needs_remain['energy']
    kg_needed -= surplus / e_yld
    if fail:
        kg_needed = 0
    return kg_needed


def mk_feeds_to_use(nr_of_groups, harvest_stores):
    """
    Construct list of different crops to use for feeding.

    Parameters
    ----------
    nr_of_groups : int
        Indicates current priority in crop types being considered for feed.
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    feeds_to_use : list
        feed names being used.
    """
    feeding_priority = gd.plant_data['feeding_priority']
    feeds_to_use = gd.plant_data.index
    feeds_to_use = feeds_to_use.where(feeding_priority <= nr_of_groups)
    feeds_to_use = feeds_to_use.where(feeding_priority != 0)
    feeds_to_use = feeds_to_use.where(harvest_stores > 0)
    if len(feeds_to_use) > 1:
        feeds_to_use = feeds_to_use.drop(None)
    feeds_to_use = list(feeds_to_use)
    return feeds_to_use


def mk_yields_from_groups(nr_of_groups, harvest_stores):
    """
    Determine nutrient yields of current crop selection considered for feed.

    Parameters
    ----------
    nr_of_groups : int
        Indicates current priority in crop types being considered for feed.

    Returns
    -------
    feed_yields : pd.Series
        Contains the nutrient yields (protein, energy and dry matter) of the
        current crop selection considered for feed.
    """
    feeds_in_use = mk_feeds_to_use(nr_of_groups, harvest_stores)
    feeds = harvest_stores.loc[feeds_in_use]
    prot_stats = gd.plant_data['feed_protein_content'].loc[feeds_in_use]
    energy_stats = gd.plant_data['feed_energy_content'].loc[feeds_in_use]
    prot_yield = sum(feeds * prot_stats)
    energy_yield = sum(feeds * energy_stats)
    dm_yield = sum(feeds)
    feed_yields = {'protein': prot_yield,
                   'energy': energy_yield,
                   'dm': dm_yield}
    feed_yields = pd.Series(feed_yields)
    return feed_yields


def determine_feeding_groups(feed_needs, harvest_stores):
    """
    Determine the amount of feeding groups needed to satisfy feed needs.

    Parameters
    ----------
    feed_needs : pd.Series
        Countains the minimal nutrient needs for the current herd of animals.

    Returns
    -------
    groups_considered : int
        specifies the priority ranking up to which certain crops will be
        considered for feed purposes.
    """
    need_met = False
    groups_considered = 1
    feed_yields = mk_yields_from_groups(groups_considered, harvest_stores)
    if feed_yields['protein'] >= feed_needs['protein']:
        if feed_yields['energy'] >= feed_needs['energy']:
            if feed_yields['dm'] >= feed_needs['dm']:
                need_met = True

    while not need_met:
        groups_considered += 1
        if groups_considered > max(gd.plant_data['feeding_priority']):
            groups_considered = 0
            break
        feed_yields = mk_yields_from_groups(groups_considered, harvest_stores)
        if feed_yields['protein'] >= feed_needs['protein']:
            if feed_yields['energy'] >= feed_needs['energy']:
                if feed_yields['dm'] >= feed_needs['dm']:
                    need_met = True

    return groups_considered


def mk_feed_needs(animals_on_farm):
    """
    Determine nutrient needs of current herd.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    herd_feed_needs : pd.Series
    Countains the minimal nutrient needs for the current herd of animals.
    """
    herd_prot_req = sum(animals_on_farm *
                        gd.animal_data['protein_requirement'])
    herd_mj_req = sum(animals_on_farm *
                      gd.animal_data['feed_energy_requirement'])
    herd_dm_req = sum(animals_on_farm * gd.animal_data['DM_requirement'])
    herd_feed_needs = {'protein': herd_prot_req,
                       'energy': herd_mj_req,
                       'dm': herd_dm_req}
    herd_feed_needs = pd.Series(herd_feed_needs)
    return herd_feed_needs


def mk_feed_limits(animals_on_farm):
    """
    Determine the nutrient limits that could be fed to the herd.

    Parameters
    ----------
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    herd_feed_ceils : pd.Series
        Contains the maxium nutrient amounts the herd could be fed.
    """
    herd_prot_ceil = sum(animals_on_farm * gd.animal_data['protein_limit'])
    herd_energy_ceil = sum(animals_on_farm *
                           gd.animal_data['feed_energy_limit'])
    herd_dm_ceil = sum(animals_on_farm * gd.animal_data['DM_limit'])
    herd_feed_ceils = {'protein': herd_prot_ceil,
                       'energy': herd_energy_ceil,
                       'dm': herd_dm_ceil}
    herd_feed_ceils = pd.Series(herd_feed_ceils)
    return herd_feed_ceils


def mk_yields_from_feed(label, amount, source_data):
    """
    Determine nutrient yields of given crop in specified amount.

    Parameters
    ----------
    label : str
        Name of the crop being fed.
    amount : float
        Kg amount of the crop being fed.
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.

    Returns
    -------
    feed_yields : pd.Series
        Contains the nutrient yields (protein, energy and dry matter) of the
        current crop selection considered for feed.
    """
    prot_yield = source_data['feed_protein_content'].loc[label] * amount
    energy_yield = source_data['feed_energy_content'].loc[label] * amount
    dm_yield = amount

    feed_yields = {'protein': prot_yield,
                   'energy': energy_yield,
                   'dm': dm_yield}
    feed_yields = pd.Series(feed_yields)
    return feed_yields


def find_la(nutris, feed_needs_remain, harvest_stores):
    """
    Find label and amount of crop to feed at this step in the agorithm.

    Parameters
    ----------
    nutris : NutrientData
        Class constructed with all relevant nutrient data for this function.
    feed_needs_remain : pd.Series
        Countains the minimal nutrient needs for the current herd of animals at
        this stage in the feeding algorithm.
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.

    Returns
    -------
    label : str
        Name of the crop to feed.
    amount : float
        Kg amount of the crop to feed.
    """
    if nutris.p_kg == nutris.first:
        if nutris.kg_tf * nutris.p_yld > (feed_needs_remain['protein'] + 1):
            nutris.kg_tf = feed_needs_remain['protein'] / nutris.p_yld / 100
            if nutris.kg_tf < 1:
                nutris.kg_tf *= 100
        if nutris.kg_tf > harvest_stores[nutris.p_lab]:
            nutris.kg_tf = harvest_stores[nutris.p_lab]
        label = nutris.p_lab
        amount = nutris.kg_tf
    if nutris.e_kg == nutris.first:
        if nutris.kg_tf * nutris.e_yld > (feed_needs_remain['energy'] + 1):
            nutris.kg_tf = feed_needs_remain['energy'] / nutris.e_yld / 100
            if nutris.kg_tf < 1:
                nutris.kg_tf *= 100
        if nutris.kg_tf > harvest_stores[nutris.e_lab]:
            nutris.kg_tf = harvest_stores[nutris.e_lab]
        label = nutris.e_lab
        amount = nutris.kg_tf
    if nutris.dm_kg == nutris.first:
        if nutris.kg_tf > harvest_stores[nutris.dm_lab]:
            nutris.kg_tf = harvest_stores[nutris.dm_lab]
        label = nutris.dm_lab
        amount = nutris.kg_tf
    return label, amount


def get_grasses(feed_sources):
    """
    Get the grasses present in feed sources.

    Parameters
    ----------
    feed_sources : list
        Names of the crops being considered for feed.

    Returns
    -------
    grasses : list
        Names of those crops which can be considered grasses.
    """
    grasses = []
    for crop in feed_sources:
        if re.search(r'[Gg]rass', crop):
            grasses.append(crop)
    return grasses


def rm_grasses(feed_sources):
    """
    Make a list of feed sources where grasses are removed.

    Parameters
    ----------
    feed_sources : list
        Names of the crops being considered for feed.

    Returns
    -------
    feed_sources : list
        Names of the crops being considered for feed. Now without grasses.
    """
    grasses = get_grasses(feed_sources)
    for grass in grasses:
        pos = feed_sources.index(grass)
        feed_sources.pop(pos)
    return feed_sources


def under_grass(feed_use, grasses, amount):
    """
    Calculate grass that can be fed before pasture/barn ratio exceeds.

    Parameters
    ----------
    feed_use : pd.Series
        Contains the kg amount determined for feed for each crop.
    grasses : list
        Names of those crops which can be considered grasses..
    amount : float
        amount of crop/grass wanting to be fed.

    Returns
    -------
    amount : float
        amount of crop/grass to be fed after limit is applied
    """
    # Maybe add barn time to estate in future.
    max_grass = (sum(feed_use) + amount) * (173 / 365)
    grass_yield = sum(feed_use[grasses]) + amount
    while grass_yield > max_grass:
        if grass_yield - max_grass > 1200:
            amount -= 600
        else:
            amount -= 50
        max_grass = (sum(feed_use) + amount) * (173 / 365)
        grass_yield = sum(feed_use[grasses]) + amount
        if amount < 0:
            amount = 0
            break
    return amount


def check_margin(feed, feed_needs, feed_limits, source_data):
    """
    Check if current feed proposed fits within nutrient limits.

    Parameters
    ----------
    feed : pd.Series
        Contains the kg amount considered for feed for each crop.
    feed_needs : pd.Series
        Contains the minimum required amount of nutrients in this feeding step.
    feed_limits : pd.Series
        Containing the maximum amount of nutrients that may be fed in this
        feeding step.
    source_data : pd.Dataframe
        Data frame containing all attributes relevant to selection of feed.

    Returns
    -------
    bool
        True if given feed amount fits within nutrient limits specified.
        False if not.
    """
    prot_yield = sum(feed * source_data['feed_protein_content'])
    energy_yield = sum(feed * source_data['feed_energy_content'])
    dm_yield = sum(feed)
    if feed_limits['protein'] >= prot_yield >= feed_needs['protein']:
        if feed_limits['energy'] >= energy_yield >= feed_needs['energy']:
            if feed_limits['dm'] >= dm_yield >= feed_needs['dm']:
                return True
    return False


def find_feed_optim(harvest_stores, feed_needs, feed_limits,
                    feeding_groups_used):
    """
    Find a feed composition optimised in meeting nutrient requirements.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    feed_needs : pd.Series
        Countains the minimal nutrient needs for the current herd of animals at
        this stage in the feeding algorithm.
    feed_limits : pd.Series
        Contains the maxium nutrient amounts the herd could be fed at this
        stage in the feeding algorithm.
    feeding_groups_used : int
        The priority ranking up to which certain crops will be considered for
        feed purposes.

    Returns
    -------
    feed_use : pd.Series
        Contains the kg amount determined for feed for each crop.
    """
    harvest_stores = harvest_stores.copy()
    feed_use = pd.Series(0.0, index=harvest_stores.index)
    feed_sources = mk_feeds_to_use(feeding_groups_used, harvest_stores)
    feed_sources = rm_grasses(feed_sources)
    source_data = gd.plant_data.loc[feed_sources]
    feed_needs_remain = feed_needs.copy()
    feed_limits_remain = feed_limits.copy()
    skip_grass = False

    # As long as feed does not match nutrient requirement add extra feed.
    while not check_margin(feed_use, feed_needs, feed_limits, gd.plant_data):
        # If no feed sources are left, no proper feed amount could be found
        # this iteration.
        if len(feed_sources) == 0:
            feed_needs_remain = feed_needs.copy()
            feed_limits_remain = feed_limits.copy()
            feed_use[:] = 0
            break
        nutris = NutrientData(source_data, feed_needs_remain, harvest_stores)
        # If no feed needs are left, we overfed on feed limits; no proper feed
        # amount could be found this iteration.
        if nutris.first <= 0:
            feed_needs_remain = feed_needs.copy()
            feed_limits_remain = feed_limits.copy()
            feed_use[:] = 0
            break
        # Get amount and crop kind to add to feed.
        label, amount = find_la(nutris, feed_needs_remain, harvest_stores)
        # If we can't consider grass for feed this step, make sure we don't
        # add too much feed.
        if skip_grass and amount > 100:
            amount /= 10
        skip_grass = False
        grasses = get_grasses(feed_sources)
        # If we're trying to feed grass, make sure we're not feeding it while
        # animals would be in the barn.
        if label in grasses:
            max_grass = (sum(feed_use) + amount) * (173 / 365)
            if sum(feed_use[grasses]) + amount > max_grass:
                amount = under_grass(feed_use, grasses, amount)
                skip_grass = True
        # apply amount and crop to feed.
        amount = np.ceil(amount)
        feed_use[label] += amount
        nutri_yields_part = mk_yields_from_feed(label, amount, source_data)
        feed_needs_remain -= nutri_yields_part
        feed_limits_remain -= nutri_yields_part
        harvest_stores[label] -= amount
        feed_sources = mk_feeds_to_use(feeding_groups_used, harvest_stores)
        # If animals are in barn remove grasses from feeds to consider.
        if skip_grass:
            feed_sources = rm_grasses(feed_sources)
        source_data = gd.plant_data.loc[feed_sources]
    return feed_use, feed_limits_remain


def feed_animals(harvest_stores, animals_on_farm):
    """
    Calculate which crop products to feed to the animals.

    Parameters
    ----------
    harvest_stores : pd.Series
        Contains all harvested crops and their stored amounts.
    animals_on_farm : pd.Series
        Keeps track of which animals are on the farm and in what amount they
        are present.

    Returns
    -------
    feed_use : pd.Series
        Contains the kg amount determined for feed for each crop.
    """
    feed_needs = mk_feed_needs(animals_on_farm)
    feeding_groups_used = determine_feeding_groups(feed_needs, harvest_stores)
    # While harvest stores cannot meet feed needs reduce herd size.
    while feeding_groups_used == 0:
        al.reduce_animal(animals_on_farm)
        feed_needs = mk_feed_needs(animals_on_farm)
        feeding_groups_used = determine_feeding_groups(feed_needs,
                                                       harvest_stores)
    feed_limits = mk_feed_limits(animals_on_farm)
    feed_use = pd.Series(0.0, index=harvest_stores.index)

    # Try to find feed composition meeting nutrient boundries.
    while sum(feed_use) == 0 and\
            feeding_groups_used <= max(gd.plant_data['feeding_priority']):
        harvest_stores_temp = harvest_stores.copy()
        feed_limits_temp = feed_limits.copy()
        feed_needs_temp = feed_needs.copy()
        feed_use, feed_limits_remain =\
            find_feed_optim(harvest_stores_temp, feed_needs_temp,
                            feed_limits_temp, feeding_groups_used)
        feeding_groups_used += 1

    feeding_groups_used -= 1
    minimal_herd = gd.estate_values['female_ratio'] * 3 +\
        gd.estate_values['male_ratio'] * 2
    # If no feed composition can be found reduce herd size to try and solve it.
    while sum(feed_use) == 0 and sum(animals_on_farm) > minimal_herd:
        al.reduce_animal(animals_on_farm)
        # maybe base reduce animal on overfeeding (feed_limit_remain)?
        feed_needs = mk_feed_needs(animals_on_farm)
        feed_limits = mk_feed_limits(animals_on_farm)
        harvest_stores_temp = harvest_stores.copy()
        feed_use, feed_limits_remain =\
            find_feed_optim(harvest_stores_temp, feed_needs, feed_limits,
                            feeding_groups_used)
    if sum(feed_use) == 0:
        print('could not meet herd diet restraints')
    return feed_use
