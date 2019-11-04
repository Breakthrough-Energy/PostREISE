import seaborn as sns

ZONES = {
    'Western': ['Arizona', 'California', 'Colorado', 'Idaho', 'Montana Western', 'Nevada', 'New Mexico Western', 'Oregon', 'Utah','Washington', 'Wyoming', 'El Paso', 'Western'],
    'Texas': ['Far West', 'North', 'West', 'South', 'North Central', 'South Central', 'Coast', 'East', 'Texas']
}
SCENARIO_RESOURCE_TYPES = ['wind', 'solar', 'ng', 'coal', 'nuclear', 'geothermal', 'hydro']
ALL_RESOURCE_TYPES = SCENARIO_RESOURCE_TYPES + ['other inc. biomass']
RESOURCE_LABELS = {'wind': 'Wind', 'solar': 'Solar', 'ng': 'Natural Gas', 'coal': 'Coal', 'nuclear': 'Nuclear', 'geothermal': 'Geothermal', 'hydro': 'Hydro', 'other inc. biomass': 'Other inc. Biomass'}
RESOURCE_COLORS = type2color = {
    'wind': sns.xkcd_rgb["green"],
    'solar': sns.xkcd_rgb["amber"],
    'hydro': sns.xkcd_rgb["light blue"],
    'ng': sns.xkcd_rgb["orchid"],
    'nuclear': sns.xkcd_rgb["silver"],
    'coal': sns.xkcd_rgb["light brown"],
    'other inc. biomass': 'rebeccapurple',
    'other': 'royalblue'
}