import matplotlib.pyplot as plt
import pandas as pd
import sys

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
            element is the timezone, only UTC, PST and LT (local time) are \ 
            possible. 4th element is the frequency for resampling, can be \
            *'D'*, *'W'* or *'auto'*.
        :param list zones: geographical zones. Any combinations of \ 
            *'Arizona'*, *'California'*, *'Bay Area'*, \ 
            *'Central California'*, *'Northern California'*, \ 
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
        
        # Check parameters
        self._check_dates(time[0], time[1])
        self._check_zones(zones)
        self._check_resources(resources)
        self._check_tz(time[2])
        self._check_freq(time[3])

        # Set attributes
        self.tz = time[2]
        self.freq = time[3]
        self.zones = zones
        self.resources = resources
        self.normalize = normalize
        self.zone2time = {'Arizona': [-7, 'MST'],
                          'Bay Area': [-8, 'PST'],
                          'California': [-8, 'PST'],
                          'Central California': [-8, 'PST'],
                          'Colorado': [-7, 'MST'],
                          'El Paso': [-7, 'MST'],
                          'Idaho': [-7, 'MST'],
                          'Montana': [-7, 'MST'],
                          'Nevada': [-7, 'MST'],
                          'New Mexico': [-7, 'MST'],
                          'Northern California': [-8, 'PST'],
                          'Oregon': [-8, 'PST'],
                          'Southeast California': [-8, 'PST'],
                          'Southwest California': [-8, 'PST'],
                          'Utah': [-7, 'MST'],
                          'Washington': [-8, 'PST'],
                          'Western': [-8, 'PST'],
                          'Wyoming': [-7, 'MST']}
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

        if self.freq == 'auto':
            self._set_frequency(pd.Timestamp(time[0]), pd.Timestamp(time[1]))

        if kind == "stacked":
            self.data = []
            self.grid.read_demand_data()
            for z in zones:
                self._set_date_range(pd.Timestamp(time[0]),
                                     pd.Timestamp(time[1]),
                                     pd.Timedelta(hours=self.zone2time[z][0]))
                self.data.append(self._get_stacked(z))

        elif kind == "comp":
            if self.tz == 'LT':
                print('PST is set for all zones')
                self.tz = 'PST'
            self._set_date_range(pd.Timestamp(time[0]),
                                 pd.Timestamp(time[1]),
                                 pd.Timedelta(hours=-8))
            self.data = []
            for r in resources:
                self.data.append(self._get_comp(r))

    def _check_dates(self, start_date, end_date):
        """Test dates.

        :param string start_date: starting date
        :param string end_date: ending date
        """
        try:
            self.PG.loc[start_date]
            self.PG.loc[end_date]
        except KeyError:
            print("Dates must be within [%s,%s]" % (self.PG.index[0],
                  self.PG.index[-1]))
            sys.exit('Error')

    def _check_zones(self, zones):
        """Test zones.

        :param list zones: geographical zones.
        """
        all = list(self.grid.load_zones.values()) + ['California', 'Western']
        for z in zones:
            if z not in all:
                print("%s is incorrect. Possible zones are:" % all)
                sys.exit('Error')

    def _check_resources(self, resources):
        """Test resources.

        :param list resources: type of generators.
        """
        all = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']
        for r in resources:
            if r not in all:
                print("%s is incorrect. Possible resources are:" % all)
                sys.exit('Error')

    def _check_tz(self, tz):
        """Test time zone.

        :param string tz: time zone.
        """
        all = ['LT', 'PST', 'UTC']
        if tz not in all:
            print("%s is incorrect. Possible time zones are:" % all)
            sys.exit('Error')

    def _check_freq(self, freq):
        """Test freq.

        :param string freq: frequency for resampling.
        """
        all = ['H', 'D', 'W', 'auto']
        if freq not in all:
            print("%s is incorrect. Possible frequency are:" % all)
            sys.exit('Error')

    def _to_LT(self, df_utc, zone):
        """Converts UTC time to Local Time.

        :param pandas df_utc: data frame with UTC timestamp as indices.
        :param string zone: one of the zones.
        :param return: data frame with Local Time timestamp as indices.
        """
        df_lt = df_utc.set_index(df_utc.index +
                                 pd.Timedelta(hours=self.zone2time[zone][0]))
        df_lt.index.name = self.zone2time[zone][1]

        return df_lt

    def _to_PST(self, df_utc):
        """Converts UTC time to PST.
    
        :param pandas df_utc: data frame with UTC timestamp as indices.
        :param return: data frame with PST timestamp as indices.
        """
        df_pst = df_utc.set_index(df_utc.index - pd.Timedelta(hours=8))
        df_pst.index.name = 'PST'
        
        return df_pst

    def _set_frequency(self, start_date, end_date):
        """Sets frequency for resampling.

        :param pandas start_date: starting timestamp.
        :param pandas end_date: ending timestamp.
        """

        delta = start_date - end_date

        if delta.days < 7:
            self.freq = 'H'
        elif delta.days > 31 and delta.days < 180:
            self.freq = 'D'
        else:
            self.freq = 'W'

    def _set_date_range(self, start_date, end_date, offset):
        """Calculates the appropriate date range after resampling in order to \ 
            to get an equal number of entries per sample.

        :param pandas start_date: starting timestamp.
        :param pandas end_date: ending timestamp.
        :param pandas offset: UTC offset
        """

        last = pd.Timestamp(self.PG.index[-1]) + offset

        timestep = pd.DataFrame(index=pd.date_range(
            start_date + offset, end_date + offset, freq='H')).resample(
            self.freq, label='left').size().rename('Number of Hours')

        if self.freq == 'H':
            self.from_index = start_date
            self.to_index = timestep.index[-1] if end_date > last else end_date
        elif self.freq == 'D' or self.freq == 'W':
            self.from_index = timestep.index.values[0] if \
                timestep[0] == timestep[1] else timestep.index[1]
            self.to_index = timestep.index.values[-1] if \
                timestep[-1] == timestep[-2] else timestep.index[-2]

        self.timestep = timestep[self.from_index:self.to_index]

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
        if self.normalize:
            ax.set_ylabel('Normalized Generation', fontsize=20)
        else:
            ax.set_ylabel('Generation (MWh)', fontsize=20)
        
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
                PG = self._to_LT(PG, zone)
            elif self.tz == 'PST':
                PG = self._to_PST(PG)

            return PG.resample(self.freq, label='left').sum()[
                self.from_index:self.to_index], capacity

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
            demand = self._to_LT(demand, zone)
        elif self.tz == 'PST':
            demand = self._to_PST(demand)

        return demand.resample(self.freq, label='left').sum()[
            self.from_index:self.to_index]
    
    def _get_stacked(self, zone):
        """Calculates time series of PG and demand for one zone. 

        :param string zone: zone to consider.
        :return: time series of PG and demand for selected zone and axis \ 
            object containing information to plot. 
        """

        fig = plt.figure(figsize=(20, 10))
        plt.title('%s' % zone, fontsize=22)
        ax = fig.gca()
        
        demand = self._get_demand(zone)
        
        PG, capacity = self._get_PG(zone, self.resources)
        if PG is not None:
            PG_groups = PG.T.groupby(self.grid.genbus['type'])
            PG_stack = PG_groups.agg(sum).T
            type2label = self.type2label.copy()
            for type in self.grid.ID2type.values():
                if type not in PG_stack.columns:
                    del type2label[type]

            if self.normalize is True:
                PG_stack = PG_stack.divide(capacity * self.timestep, 
                                           axis='index')
                demand = demand.divide(capacity * self.timestep, axis='index')

            ax = PG_stack[list(type2label.keys())].rename(
                columns=type2label).plot.area(
                color=[self.grid.type2color[r] for r in type2label.keys()], 
                alpha=0.7, ax=ax)
            demand.plot(color='red', lw=4, ax=ax)
        
            ax.set_ylim([0, max(ax.get_ylim()[1], 1.1*demand.max().values[0])])

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

        fig = plt.figure(figsize=(20, 10))
        plt.title('%s' % resource.capitalize(), fontsize=22)
        ax = fig.gca()
        
        first = True
        for z in self.zones:
            PG, capacity = self._get_PG(z, [resource])
            if PG is None:
                pass
            else:
                col_name = '%s: %d plants (%d MW)' % (z, PG.shape[1], capacity)
                total_tmp = pd.DataFrame(PG.T.sum().rename(col_name))

                if self.normalize:
                    total_tmp = total_tmp.divide(capacity * self.timestep, 
                                                 axis='index')

                if first:
                    total = total_tmp
                    first = False
                else:
                    total = pd.merge(total, total_tmp, left_index=True, 
                                     right_index=True)

                total[col_name].plot(color=self.zone2style[z]['color'],
                                     alpha=self.zone2style[z]['alpha'],
                                     lw=self.zone2style[z]['lw'],
                                     ls=self.zone2style[z]['ls'],
                                     ax=ax)

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
