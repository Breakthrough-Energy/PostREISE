from datetime import datetime, timedelta


class PlotRun():
    """Generates plots of power generated.

    """

    def __init__(self, run, from_index, to_index, zones, resources, kind, 
                 freq='auto'):
        """Initializes class instance.

        :param tuple run: first element is a data frame of the power \ 
            generated with id of the plants as columns and UTC timestamp \ 
            as indiced. Second element is a grid instance.
        :param string from_index: starting UTC timestamp.
        :param string to_index: ending UTC timestamp.
        :param list zones: any combinations of *Arizona*, *California*, \ 
            *Bay Area*, *Central California*, *Northern California*, \ 
            *Southeast California*, *Southwest California*, *Colorado*, \ 
            *El Paso*, *Idaho*, *Montana*, *Nevada*, *New Mexico*, *Oregon*, \ 
            *Utah*, *Washington*, *Western*, *Wyoming*.
        :param list resources: energy resources. Can be any combinations of \ 
            *coal*, *hydro*, *ng*, *nuclear*, *solar*, *wind*.
        :param string kind: one of *stacked*, *curtailment*, *zones*, \ 
            *plants*, *correlation*
        :param string freq: frequency for resampling. Can be 'D', 'W', 'M'.
        """

        self.PG = run[0][from_index:to_index]
        self.grid = run[1]
        self.from_index = from_index
        self.to_index = to_index
        self.zones = zones
        self.resources = resources
        self.freq = freq

        if self.freq = 'auto':
            self._set_freq()

        if kind == "stacked":
            self.data = []
            for z in zones:
                self.data.append(self._get_stacked(z))

    def _set_freq(self):
        """Sets frequency for resampling.

        """

        delta = datetime.strptime(to_index, '%Y-%m-%d-%H') - \
            datetime.strptime(from_index, '%Y-%m-%d-%H')

        if delta.days < 7:
            self.freq = 'H'
        elif delta.days >= 7 and delta.days < 180:
            self.freq = 'D'
        else:
            self.freq = 'W'

    _type2label = {'nuclear': 'Nuclear', 'hydro': 'Hydro', 'coal': 'Coal',
                   'ng': 'Natural Gas', 'solar': 'Solar', 'wind': 'Wind'}

    def self._get_stacked(self, zone):
        """Calculate time series of PG of stacked resources for one zone. 
        
        :param string zone: zone to consider.
        :return: resampled time series of stacked resources for selected zone.
        """
        plant_id = []
        for r in self.resources:
            plant_id += self._get_plant_id(zone, r)

    def self._get_plant_id(self, zone, resource):
        """Extracts the plant identification number of all the generators \ 
            located in one zone and using one specific resource.
        
        :param string zone: zone to consider.
        :param list resources: type of generators to consider.
        :return: plant identification number of all the generators located \ 
            in the specified zone and using the specified resource. 
        """

        if zone not in sel.grid.load_zones.values():
            if zone == 'Western':
                id = self.grid.genbus.index
            elif zone == 'California':
                CA = ['Bay Area', 'Central California', 'Northern California',
                      'Southeast California', 'Southwest California']
                id = []
                for load_zone in CA:
                    id += self.grid.genbus.groupby(
                        ['ZoneName', 'type']).get_group(
                        load_zone, resource).index.values.tolist()
            else:
                print('Possible zones are:')
                print(self.grid.load_zones.values())
                return
        else:
            id = self.grid.genbus.groupby(['ZoneName', 'type']).get_group(
                zone, resource).index

        return id
