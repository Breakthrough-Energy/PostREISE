import seaborn as sns

ZONES = {
    'Western': ['Arizona', 'California', 'Colorado', 'Idaho', \
                'Montana Western', 'Nevada', 'New Mexico Western', 'Oregon', \
                'Utah', 'Washington', 'Wyoming', 'El Paso', 'Western'],
    'Texas': ['Far West', 'North', 'West', 'South', 'North Central', \
              'South Central', 'Coast', 'East', 'Texas']
}
SCENARIO_RESOURCE_TYPES = ['wind', 'solar', 'ng',
                           'coal', 'nuclear', 'geothermal', 'hydro']
ALL_RESOURCE_TYPES = SCENARIO_RESOURCE_TYPES + ['other inc. biomass']
RESOURCE_LABELS = {'wind': 'Wind', 'solar': 'Solar', 'ng': 'Natural Gas', \
                   'coal': 'Coal', 'nuclear': 'Nuclear',
                   'geothermal': 'Geothermal', 'hydro': 'Hydro', \
                   'other inc. biomass': 'Other inc. Biomass'}
RESOURCE_COLORS = {
    'wind': sns.xkcd_rgb["green"],
    'solar': sns.xkcd_rgb["amber"],
    'hydro': sns.xkcd_rgb["light blue"],
    'ng': sns.xkcd_rgb["orchid"],
    'nuclear': sns.xkcd_rgb["silver"],
    'coal': sns.xkcd_rgb["light brown"],
    'geothermal': sns.xkcd_rgb["hot pink"],
    'dfo': sns.xkcd_rgb["royal blue"],
    'storage': sns.xkcd_rgb["orange"],
    'other inc. biomass': 'rebeccapurple',
    'other': 'royalblue'
}
SHADOW_PRICE_COLORS = ['darkmagenta' ,'blue', '#66bd63', '#d9ef8b', 'gold', '#fdae61', '#f46d43', '#d73027', 'darkred']
BASELINES = {
    'Arizona': 4.567094,
    'California': 81.0,
    'Colorado': 11.039050999999999,
    'Idaho': 2.5057110000000002,
    'Montana Western': 2.28368,
    'Nevada': 7.047959,
    'New Mexico Western': 2.5586450000000003,
    'Oregon': 7.509413,
    'Utah': 2.798768,
    'Washington': 96.129826,
    'Wyoming': 5.9288989999999995,
    'El Paso': 0.021684000000000002,
    'Western': 223.369046}
CA_BASELINES = {
    'Arizona': 4.567094,
    'California': 81.0,
    'Colorado': 11.039050999999999,
    'Idaho': 2.5057110000000002,
    'Montana Western': 2.28368,
    'Nevada': 7.047959,
    'New Mexico Western': 2.5586450000000003,
    'Oregon': 7.509413,
    'Utah': 2.798768,
    'Washington': 7.24,
    'Wyoming': 5.9288989999999995,
    'El Paso': 0.021684000000000002,
    'Western': 191.34526}
TARGETS = {
    'Arizona': 14.556582999999998,
    'California': 203.49599999999998,
    'Colorado': 18.892801000000002,
    'Idaho': 0.0,
    'Montana Western': 2.248663,
    'Nevada': 20.942648000000002,
    'New Mexico Western': 9.613257,
    'Oregon': 13.704619000000001,
    'Utah': 6.94292,
    'Washington': 95.334513,
    'Wyoming': 0.0,
    'El Paso': 0.0,
    'Western': 385.732004}
CA_TARGETS = {
    'Arizona': 58.22633199999999,
    'California': 203.49599999999998,
    'Colorado': 37.785602000000004,
    'Idaho': 23.28269,
    'Montana Western': 8.994652,
    'Nevada': 25.131178,
    'New Mexico Western': 11.535909,
    'Oregon': 32.891086,
    'Utah': 20.828761,
    'Washington': 71.500885,
    'Wyoming': 11.379466,
    'El Paso': 0.0,
    'Western': 505.052561}
DEMAND = {
    'Arizona': 97.04388686,
    'California': 339.16,
    'Colorado': 62.97600378,
    'Idaho': 38.80448402,
    'Montana Western': 14.991087099999998,
    'Nevada': 41.88529659,
    'New Mexico Western': 19.22651448,
    'Oregon': 54.81847715,
    'Utah': 34.71460116,
    'Washington': 119.16814099999999,
    'Wyoming': 18.96577653,
    'El Paso': 0.0,
    'Western': 841.7542689999999}
