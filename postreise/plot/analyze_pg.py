from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd


class AnalyzePG():
    """Manipulates PG.

    """

    def __init__(self, run, time, zones, resources, kind, normalize=False):
        """Initializes class instance.

        :param tuple run: run related parameters. 1st element is a data frame \ 
            of the power generated with id of the plants as columns and UTC \ 
            timestamp as indices. 2nd element is a grid instance.
        :param tuple time: time related parameters. 1st element is the \ 
            starting date. 2nd element is the ending date (left out). 3rd \ 
            element is the timezone, only UTC or LT (local time) are \ 
            possible. 4th element is the frequency for resampling, can be \
            *'D'*, *'W'* or *'auto'*.
        :param list zones: any combinations of *'Arizona'*, *'California'*, \ 
            *'Bay Area'*, *'Central California'*, *'Northern California'*, \ 
            *'Southeast California'*, *'Southwest California'*, *'Colorado'*, \ 
            *'El Paso'*, *'Idaho'*, *'Montana'*, *'Nevada'*, *'New Mexico'*, \ 
            ''*Oregon'*, *'Utah'*, *'Washington'*, *'Western'*, *'Wyoming'*.
        :param list resources: energy resources. Can be any combinations of \ 
            *'coal'*, *'hydro'*, *'ng'*, *'nuclear'*, *'solar'*, *'wind'*.
        :param string kind: one of *'stacked'*, *'curtailment'*, *'comp'*, \ 
            *'plants'*, *'correlation'*
        :param bool normalize: should net generation be normalized by capacity.
        """

        self.PG = run[0]
        self.grid = run[1]
        self.from_index = time[0]
        self.to_index = time[1]
        self.tz = time[2]
        self.freq = time[3]
        self.zones = zones
        self.resources = resources
        self.normalize = normalize

        # Check parameters
        self._check_dates()
        self._check_zones()
        self._check_resources()

        if self.freq == 'auto': self._set_frequency() 

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
            if self.tz == 'LT':
                print('PST is used for all zones')
            self.data = []
            for r in resources:
                self.data.append(self._get_comp(r))

    def _check_dates(self):
        """Tests dates.

        """
        try:
            self.PG.loc[self.from_index]
            self.PG.loc[self.to_index]
        except KeyError:
            print("Dates must be within [%s,%s]" % (self.PG.index[0],
                  self.PG.index[-1]))

    def _check_zones(self):
        """Tests the zones.

        """
        all = list(self.grid.load_zones.values()) + ['California', 'Western']
        for z in self.zones:
            if z not in all:
                print("%s is incorrect. Possible zones are:" % all)
                return

    def _check_resources(self):
        """Tests the resources.

        """
        all = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']
        for r in self.resources:
            if r not in all:
                print("%s is incorrect. Possible resources are:" % all)
                return

    def _to_LT(self, df_utc, zone):
        """Converts UTC time to Local Time.

        :param pandas df_utc: data frame with UTC timestamp as indices.
        :param return: data frame with Local Time as indices.
        """
        df_lt = df_utc.set_index(df_utc.index -
                                 timedelta(hours=self.zone2time[zone][0]))
        df_lt.index.name = self.zone2time[zone][1]

        return df_lt

    def _set_frequency(self):
        """Sets frequency for resampling.

        """

        delta = datetime.strptime(self.to_index, '%Y-%m-%d-%H') - \
            datetime.strptime(self.from_index, '%Y-%m-%d-%H')

        if delta.days < 7:
            self.freq = 'H'
        elif delta.days > 31 and delta.days < 180:
            self.freq = 'D'
        else:
            self.freq = 'W'

    def _get_plant_id(self, zone, resource):
        """Extracts the plant identification number of all the generators \ 
            located in one zone and using one specific resource.

        :param string zone: zone to consider.
        :param string resource: type of generator to consider.
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

    def _get_PG(self, zone, resources):
        """Get PG of all the generators located in one zone and powered by \ 
            resources.
        
        :param string zone: one of the zones.
        :param list resources: type of generators to consider.
        :return: PG and capacity of all the generators located in one zone \ 
            and using the specified resources.
        """

        plant_id = []
        for r in resources:
            plant_id += self._get_plant_id(zone, r)

        if len(plant_id) == 0:
            print("No %s plants in %s" % ("/".join(resources), zone))
            return [None] * 2
        else:
            capacity = sum(self.grid.genbus.loc[plant_id].GenMWMax.values)
            PG = self.PG[plant_id]
            if self.tz == 'LT':
                PG = self._to_LT(PG, zone)[self.from_index:self.to_index]
            else:
                PG = PG[self.from_index:self.to_index]

            return PG, capacity
        
    def _get_demand(self, zone):
        """Get demand profile for load zone, California or total.

        :param string zone: one of the zones.
        :return: data frame of the load with selected zone as columns and UTC \ 
            timestamp as indices.
        """

        demand = self.grid.demand_data_2016
        if zone == 'Western':
            demand = demand.sum(axis=1).rename('demand').to_frame()
        elif zone == 'California':
            CA = ['Bay Area', 'Central California', 'Northern California',
                  'Southeast California', 'Southwest California']
            demand = demand.loc[:, CA].sum(axis=1).rename('demand').to_frame()
        else:
            demand = demand.loc[:, zone].rename('demand').to_frame()
            
        if self.tz == 'LT':
            return self._to_LT(demand, zone)[
                self.from_index:self.to_index].resample(self.freq).sum()
        else:
            return demand[self.from_index:self.to_index].resample(
                self.freq).sum()
            
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

        demand = self._get_demand(zone)
        
        PG, capacity = self._get_PG(zone, self.resources)
        if PG is not None:
            PG_groups = PG.T.groupby(self.grid.genbus['type'])
            PG_stack = PG_groups.agg(sum).T.resample(self.freq).sum()
            type2label = self.type2label.copy()
            for type in self.grid.ID2type.values():
                if type not in PG_stack.columns:
                    del type2label[type]

            if self.normalize is True:
                delta = PG_stack.index[1] - PG_stack.index[0]
                PG_stack /= capacity*(delta.days*24 + delta.seconds/3600)
                demand /= capacity*(delta.days*24 + delta.seconds/3600)

            fig = plt.figure(figsize=(20, 10))
            ax = fig.gca()
            ax = PG_stack[list(type2label.keys())].rename(
                columns=type2label).plot.area(
                color=[self.grid.type2color[r] for r in type2label.keys()], 
                alpha=0.7, ax=ax)
            demand.plot(color='red', lw=4, ax=ax)
        
            ax.set_ylim([0, max(ax.get_ylim()[1], 1.1*demand.max().values[0])])
            if self.normalize:
                ax.set_ylabel('Normalized Electricy Generated in %s' % zone, 
                              fontsize=20)
            else:
                ax.set_ylabel('Electricty Generated in %s (MWh)' % zone,
                              fontsize=20)

            return [PG_stack.merge(demand, left_index=True, right_index=True), 
                    ax, None]
        else:
            return [None] * 3

    def _get_comp(self, resource):
        """Calculates time series of PG for one resource. 
        
        :param string resource: resource to consider.
        :return: time series of PG for selected resource and axis object \ 
            containing information to plot. 
        """

        first = True
        for z in self.zones:
            PG, capacity = self._get_PG(z, [resource])
            if PG is None:
                pass
            else:
                col_name = '%s: %d plants (%d MW)' % (z, PG.shape[1], capacity)
                total_tmp = pd.DataFrame(PG.T.sum().resample(
                    self.freq).sum().rename(col_name))
                if self.normalize:
                    delta = total_tmp.index[1] - total_tmp.index[0]
                    total_tmp /= capacity*(delta.days*24 + delta.seconds/3600)

                if first:
                    total = total_tmp
                    fig = plt.figure(figsize=(20, 10))
                    ax = fig.gca()
                    first = False
                else:
                    total = pd.merge(total, total_tmp, left_index=True, 
                                     right_index=True)

                total[col_name].plot(color=self.zone2style[z]['color'],
                                     alpha=self.zone2style[z]['alpha'],
                                     lw=self.zone2style[z]['lw'],
                                     ls=self.zone2style[z]['ls'],
                                     ax=ax)

        if self.normalize:
            ylabel = 'Normalized %s Electricity Generated' % resource.capitalize()
        else:
            ylabel = '%s Electricity Generation (MWh)' % resource.capitalize()
        ax.set_ylabel(ylabel, fontsize=20)

        return [total, ax, None]

    def get_plot(self):
        """Plots.

        """
        for data in self.data:
            if data[1] is not None:
                ax = data[1]
                self._set_canvas(ax)

        plt.show()

    def get_data(self):
        """Returns data frame on screen.

        """
        data = [d[0] for d in self.data]
        return data
