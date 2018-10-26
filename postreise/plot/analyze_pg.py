from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd


class PlotRun():
    """Generates plots of power generated.

    """

    def __init__(self, run, from_index, to_index, zones, resources, kind, 
                 freq='auto', normalize=False):
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
        :param bool freq: should net generation be normalized by capacity.
        """

        self.PG = run[0][from_index:to_index]
        self.grid = run[1]
        self.from_index = from_index
        self.to_index = to_index
        self.zones = zones
        self.resources = resources
        self.freq = freq
        self.normalize = normalize


        # Check parameters
        self._check_zones()
        self._check_resources()

        if self.freq == 'auto':
            self._set_freq()

        self.zone2time = {'Arizona': [7, 'MST'],
                          'Bay Area': [8, 'PST'],
                          'California': [8, 'PST'],
                          'Central California': [8, 'PST'],
                          'Colorado': [7, 'MST'],
                          'El Paso': [7, 'MST'],
                          'Idaho': [7, 'MST'],
                          'Montana': [7, 'MST'],
                          'Nevada': [7, 'MST'],
                          'New Mexico': [7, 'MST'],
                          'Northern California': [8, 'PST'],
                          'Oregon': [8, 'PST'],
                          'Southeast California': [8, 'PST'],
                          'Southwest California': [8, 'PST'],
                          'Utah': [7, 'MST'],
                          'Washington': [8, 'PST'],
                          'Western': [8, 'PST'],
                          'Wyoming': [7, 'MST']}

        self.zone2style = {
            'Arizona':
                {'color': 'maroon', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Bay Area':
                {'color': 'blue', 'alpha': 0.6, 'lw': 4, 'ls': ':'},
            'California':
                {'color': 'blue', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Central California':
                {'color': 'blue', 'alpha': 0.6, 'lw': 4, 'ls': '-.'},
            'Colorado':
                {'color': 'darkorchid', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'El Paso':
                {'color': 'dodgerblue', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Idaho':
                {'color': 'magenta', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Montana':
                {'color': 'indigo', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Nevada':
                {'color': 'orange', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'New Mexico':
                {'color': 'teal', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Northern California':
                {'color': 'blue', 'alpha': 0.6, 'lw': 4, 'ls': '--'},
            'Oregon':
                {'color': 'red', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Southwest California':
                {'color': 'blue', 'alpha': 0.6, 'lw': 4, 'ls': '-+'},
            'Southeast California':
                {'color': 'blue', 'alpha': 0.6, 'lw': 4, 'ls': '-o'},
            'Utah':
                {'color': 'tomato', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Washington':
                {'color': 'green', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Western':
                {'color': 'black', 'alpha': 1, 'lw': 4, 'ls': '-'},
            'Wyoming':
                {'color': 'goldenrod', 'alpha': 1, 'lw': 4, 'ls': '-'}}

        self.type2label = {'nuclear': 'Nuclear',
                           'hydro': 'Hydro',
                           'coal': 'Coal',
                           'ng': 'Natural Gas',
                           'solar': 'Solar',
                           'wind': 'Wind'}

        if kind == "stacked":
            self.data = []
            self.grid.read_demand_data()
            for z in zones:
                self.data.append(self._get_stacked(z))

        elif kind == "comp":
            self.data = []
            for r in resources:
                self.data.append(self._get_comp(r))

    def _check_zones(self):
        all = list(self.grid.load_zones.values()) + ['California', 'Western']
        for z in self.zones:
            if z not in all:
                print("%s is incorrect. Possible zones are:" % all)
                return

    def _check_resources(self):
        all = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']
        for r in self.resources:
            if r not in all:
                print("%s is incorrect. Possible resources are:" % all)
                return

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

    def _get_plant_id(self, zone, resource):
        """Extracts the plant identification number of all the generators \ 
            located in one zone and using one specific resource.

        :param string zone: zone to consider.
        :param list resources: type of generators to consider.
        :return: plant identification number of all the generators located \ 
            in the specified zone and using the specified resource. 
        """

        id = []
        if zone == 'Western':
            try:
                id = self.grid.genbus.groupby('type').get_group(
                    resource).index.values.tolist()
            except KeyError:
                pass
        elif zone == 'California':
            CA = ['Bay Area', 'Central California', 'Northern California',
                  'Southeast California', 'Southwest California']
            for load_zone in CA:
                try:
                    id += self.grid.genbus.groupby(
                        ['ZoneName', 'type']).get_group(
                        (load_zone, resource)).index.values.tolist()
                except KeyError:
                    pass
        else:
            try:
                id = self.grid.genbus.groupby(['ZoneName', 'type']).get_group(
                    (zone, resource)).index.values.tolist()
            except KeyError:
                pass

        return id

    def _get_demand(self, zone):
        """Get demand profile for load zone, California or total.

        :param string zone: one of the zones.
        :return: data frame of the load with selected zone as columns and UTC \ 
            timestamp as indices.
        """

        utc_offset = timedelta(hours=self.zone2time[zone][0])
        tz = self.zone2time[zone][1]

        demand = self.grid.demand_data_2016[self.from_index:self.to_index]
        demand.set_index(demand.index - utc_offset, inplace=True)
        demand.index.name = tz

        if zone == 'Western':
            return demand.sum(axis=1)
        elif zone == 'California':
            CA = ['Bay Area', 'Central California', 'Northern California',
                  'Southeast California', 'Southwest California']
            return demand.loc[:, CA].sum(axis=1)
        else:
            return demand.loc[:, zone]

    def _set_canvas(self, ax):
        """Set attributes for plot.

        :param matplotlib ax: axis object.
        :return: updated axis object.
        """

        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.tick_params(labelsize=16)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size': 16},
                  loc='lower right')
        ax.set_xlabel('')

    def _get_stacked(self, zone):
        """Calculates time series of PG and demand for one zone. 

        :param string zone: zone to consider.
        :return: time series of PG and demand for selected zone and axis \ 
            object containing information to plot. 
        """

        utc_offset = timedelta(hours=self.zone2time[zone][0])
        tz = self.zone2time[zone][1]

        plant_id = []
        for r in self.resources:
            plant_id += self._get_plant_id(zone, r)

        PG = self.PG[plant_id]
        PG.set_index(PG.index - utc_offset, inplace=True)
        PG.index.name = tz

        PG_groups = PG.T.groupby(self.grid.genbus['type'])
        PG_stack = PG_groups.agg(sum).T.resample(self.freq).sum()
        type2label = self.type2label.copy()
        for type in self.grid.ID2type.values():
            if type not in PG_stack.columns:
                del type2label[type]

        demand = self._get_demand(zone).resample(self.freq).sum().rename(
            'demand')

        fig = plt.figure(figsize=(20, 10))
        ax = fig.gca()
        ax = PG_stack[list(type2label.keys())].rename(
            columns=type2label).plot.area(
            color=[self.grid.type2color[type] for type in type2label.keys()], 
            alpha=0.7, ax=ax)
        demand.plot(color='red', lw=4, ax=ax)
        ax.set_ylim([0., max(ax.get_ylim()[1], demand.max()+1000)])
        ax.set_ylabel('%s Net Generation (MWh)' % zone, fontsize=20)

        return [pd.merge(PG_stack, demand.to_frame(), left_index=True, 
                         right_index=True, how='outer'), ax, None]

    def _get_comp(self, resource):
        """Calculates time series of PG for one resource. 
        
        :param string resource: resource to consider.
        :return: time series of PG for selected resource and axis object \ 
            containing information to plot. 
        """

        utc_offset = timedelta(hours=self.zone2time['Western'][0])
        tz = self.zone2time['Western'][1]

        first = True
        for z in self.zones:
            plant_id = self._get_plant_id(z, resource)
            n_plants = len(plant_id)
            if n_plants == 0:
                print("No %s plants in %s" % (resource, z))
            else:
                PG = self.PG[plant_id]
                PG.set_index(PG.index - utc_offset, inplace=True)
                PG.index.name = tz

                capacity = sum(self.grid.genbus.loc[plant_id].GenMWMax.values)

                col_name = '%s: %d plants (%d MW)' % (z, n_plants, capacity)
                total_tmp = pd.DataFrame(PG.T.sum().resample(
                    self.freq).sum().rename(col_name))

                delta = total_tmp.index[1]-total_tmp.index[0]
                norm = capacity * delta.days * 24 if self.normalize else 1

                if first:
                    total = total_tmp/norm
                    fig = plt.figure(figsize=(20, 10))
                    ax = fig.gca()
                    total[col_name].plot(color=self.zone2style[z]['color'],
                                         alpha=self.zone2style[z]['alpha'],
                                         lw=self.zone2style[z]['lw'],
                                         ls=self.zone2style[z]['ls'],
                                         ax=ax)
                    first = False
                else:
                    total = pd.merge(total, total_tmp/norm, left_index=True,
                                     right_index=True, how='outer')
                    total[col_name].plot(color=self.zone2style[z]['color'],
                                         alpha=self.zone2style[z]['alpha'],
                                         lw=self.zone2style[z]['lw'],
                                         ls=self.zone2style[z]['ls'],
                                         ax=ax)

        if self.normalize:
            ylabel = 'Normalized %s Generation' % resource.capitalize()
        else:
            ylabel = '%s Net Generation (MWh)' % resource.capitalize()
        ax.set_ylabel(ylabel, fontsize=20)

        return [total, ax, None]

    def get_plot(self):
        """Plots.

        """
        for data in self.data:
            ax = data[1]
            self._set_canvas(ax)

        plt.show()

    def get_data(self):
        """Returns data frame on screen.

        """
        data = [d[0] for d in self.data]
        return data
