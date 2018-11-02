import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

class AnalyzePG():
    """Manipulates PG.

    """

    def __init__(self, run, time, zones, resources, kind, normalize=False):
        """Constructor.

        :param tuple run: run related parameters. 1st element is a data frame \ 
            of the power generated with id of the plants as columns and UTC \ 
            timestamp as indices. 2nd element is a grid instance.
        :param tuple time: time related parameters. 1st element is the \ 
            starting date. 2nd element is the ending date (left out). 3rd \ 
            element is the timezone, only *'utc'*, *'US/Pacific'* and \ 
            *'local'* are possible. 4th element is the frequency for \ 
            resampling, can be *'D'*, *'W'* or *'auto'*.
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
        :param bool normalize: should generation be normalized by capacity.
        """
        plt.close('all')

        self.PG = run[0].tz_localize('utc')
        self.grid = run[1]
        
        # Check parameters
        self._check_dates(time[0], time[1])
        self._check_zones(zones)
        self._check_resources(resources)
        self._check_tz(time[2])
        self._check_freq(time[3])
        self._check_kind(kind)

        # Set attributes
        self.freq = time[3]
        self.zones = zones
        self.resources = resources
        self.kind = kind
        self.normalize = normalize
        self.zone2time = {'Arizona': 'US/Mountain',
                          'Bay Area': 'US/Pacific',
                          'California': 'US/Pacific',
                          'Central California': 'US/Pacific',
                          'Colorado': 'US/Mountain',
                          'El Paso': 'US/Mountain',
                          'Idaho': 'US/Mountain',
                          'Montana': 'US/Mountain',
                          'Nevada': 'US/Mountain',
                          'New Mexico': 'US/Mountain',
                          'Northern California': 'US/Pacific',
                          'Oregon': 'US/Pacific',
                          'Southeast California': 'US/Pacific',
                          'Southwest California': 'US/Pacific',
                          'Utah': 'US/Mountain',
                          'Washington': 'US/Pacific',
                          'Western': 'US/Pacific',
                          'Wyoming': 'US/Mountain'}
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
            self._set_frequency(time[0], time[1])

        if kind == "stacked":
            self.data = []
            self.grid.read_demand_data()
            for z in zones:
                self.tz = self.zone2time[z] if time[2] == 'local' else time[2]
                self._set_date_range(time[0], time[1])
                self.data.append(self._get_stacked(z))

        elif kind == "comp":
            if time[2] == 'local':
                print('Set US/Pacific for all zones')
                self.tz = 'US/Pacific'
            else:
                self.tz = time[2]    
            self._set_date_range(time[0], time[1])
            self.data = []
            for r in resources:
                self.data.append(self._get_comp(r))

        elif kind == 'curtailment':
            for r in resources:
                if r == 'solar':
                    self.grid.read_solar_data()
                elif r == 'wind':
                    self.grid.read_wind_data()
                else:
                    print("Curtailment analysis is only for renewable energies")
            self.data = []
            self.grid.read_demand_data()
            for z in zones:
                self.tz = self.zone2time[z] if time[2] == 'local' else time[2]
                self._set_date_range(time[0], time[1])                
                for r in resources:
                    self.data.append(self._get_curtailment(z, r))

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
                print("%s is incorrect. Possible zones are: %s" % (z, all))
                sys.exit('Error')

    def _check_resources(self, resources):
        """Test resources.

        :param list resources: type of generators.
        """
        all = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']
        for r in resources:
            if r not in all:
                print("%s is incorrect. Possible resources are: %s" % (r,all))
                sys.exit('Error')

    def _check_tz(self, tz):
        """Test time zone.

        :param string tz: time zone.
        """
        all = ['utc', 'US/Pacific', 'local']
        if tz not in all:
            print("%s is incorrect. Possible time zones are: %s" % (tz, all))
            sys.exit('Error')

    def _check_freq(self, freq):
        """Test freq.

        :param string freq: frequency for resampling.
        """
        all = ['H', 'D', 'W', 'auto']
        if freq not in all:
            print("%s is incorrect. Possible frequency are: %s" % (freq, all))
            sys.exit('Error')

    def _check_kind(self, kind):
        """Test kind.

        :param string kind: type of analysis.
        """
        all = ['stacked', 'comp', 'curtailment']
        if kind not in all:
            print("%s is incorrect. Possible analysis are: %s" % (kind, all))
            sys.exit('Error')

    def _convert_tz(self, df_utc):
        """Convert dataframe fron UTC time zone to desired time zone.

        :param pandas df_utc: data frame with UTC timestamp as indices.
        :param return: data frame vonverted to desired time zone.
        """
        
        df_new = df_utc.tz_convert(self.tz)
        df_new.index.name = self.tz
        
        return df_new

    def _set_frequency(self, start_date, end_date):
        """Sets frequency for resampling.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        """

        delta = pd.Timestamp(start_date) - pd.Timestamp(end_date)

        if delta.days < 7:
            self.freq = 'H'
        elif delta.days > 31 and delta.days < 180:
            self.freq = 'D'
        else:
            self.freq = 'W'

    def _set_date_range(self, start_date, end_date):
        """Calculates the appropriate date range after resampling in \ 
            order to get an equal number of entries per sample.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        """

        last = self.PG.index[-1].tz_convert(self.tz)

        timestep = pd.DataFrame(index=pd.date_range(
            start_date, end_date, freq='H', tz='utc')).tz_convert(
            self.tz).resample(self.freq, label='left').size().rename(
            'Number of Hours')

        if self.freq == 'H':
            self.from_index = pd.Timestamp(start_date)
            self.to_index = timestep.index[-1] if \
            pd.Timestamp(end_date) > last else pd.Timestamp(end_date)
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

        if self.kind == 'stacked' or self.kind == 'comp':
            handles, labels = ax[0].get_legend_handles_labels()
            ax[0].legend(handles[::-1], labels[::-1], frameon=2,
                      prop={'size': 16}, loc='lower right')
            if self.normalize:
                ax[0].set_ylabel('Normalized Generation', fontsize=20)
            else:
                ax[0].set_ylabel('Generation (MWh)', fontsize=20)
        elif self.kind == 'curtailment':
            ax[0].set_ylabel('Curtailment [%]', fontsize=20)
            ax[1].set_ylabel('MWh', fontsize=20)
            ax[1].legend(loc='upper right', prop={'size':16})
        
        ax[0].set_facecolor('white')
        ax[0].grid(color='black', axis='y')
        ax[0].tick_params(labelsize=16)
        ax[0].set_xlabel('')
              
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
            PG = self._convert_tz(self.PG[plant_id]).resample(
                self.freq, label='left').sum()[self.from_index:self.to_index]

            return PG, capacity

    def _get_demand(self, zone):
        """Get demand profile for load zone, California or total.

        :param string zone: one of the zones.
        :return: data frame of the load.
        """

        demand = self.grid.demand_data_2016.tz_localize('utc')
        if zone == 'Western':
            demand = demand.sum(axis=1).rename('demand').to_frame()
        elif zone == 'California':
            CA = ['Bay Area', 'Central California', 'Northern California',
                  'Southeast California', 'Southwest California']
            demand = demand.loc[:, CA].sum(axis=1).rename('demand').to_frame()
        else:
            demand = demand.loc[:, zone].rename('demand').to_frame()

        demand = self._convert_tz(demand).resample(
            self.freq, label='left').sum()[self.from_index:self.to_index]

        return demand

    def _get_profile(self, zone, resource):
        """Get profile for resource.

        :param string zone: zone to consider
        :param string resource: type of generators to consider.
        :return: data frame of the power output (in MW) for the selected \ 
            resource
        """

        plant_id = self._get_plant_id(zone, resource)
        
        if len(plant_id) == 0:
            print("No %s plants in %s" % ("/".join(resources), zone))
            return None
        
        profile = eval('self.grid.'+resource+'_data_2016').tz_localize('utc')
        
        return self._convert_tz(profile[plant_id]).resample(
            self.freq, label='left').sum()[self.from_index:self.to_index]

    def _get_stacked(self, zone):
        """Calculates time series of PG and demand for one zone. 

        :param string zone: zone to consider.
        :return: time series of PG and demand for selected zone and axis \ 
            object containing information to plot. 
        """
        

        PG, capacity = self._get_PG(zone, self.resources)
        if PG is not None:
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s' % zone, fontsize=22)
            ax = fig.gca()
        
            demand = self._get_demand(zone)
            
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

            PG_stack = PG_stack.merge(demand, left_index=True, right_index=True)
            PG_stack.name = zone

            return [PG_stack, (ax, None), None]
        else:
            return [None, (None, None), None]

    def _get_curtailment(self, zone, resource):
        """Calculates time series of curtailment for one zone and one resource. 

        :param string zone: zone to consider.
        :param string resource: resource to consider.
        :return: time series of curtailment for selected zone along with and \ 
            axis object containing information to plot. 
        """

        PG, capacity = self._get_PG(zone, [resource])
        if PG is None:
            return [None, (None, None), None]
        else:
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s (%s)' % (zone, resource.capitalize()), fontsize=22)
            ax = fig.gca()
            ax_twin = ax.twinx()

            demand = self._get_demand(zone)
            available = self._get_profile(zone, resource)
        
            curtailment = pd.DataFrame(available.T.sum().rename('available'))
            curtailment['generated'] = PG.T.sum().values
            curtailment['demand'] = demand.values
        
            multiplier = 1
            curtailment['available'] *= multiplier
            curtailment['ratio'] = 100 * \
                (1 - curtailment['generated'] / curtailment['available'])
        
            # Deal with numerical precision
            curtailment.loc[abs(curtailment['ratio']) < 0.5, 'ratio'] = 0
            
            curtailment['ratio'].plot(ax=ax,
                legend=False, style='b', lw=4, fontsize=18, alpha=0.7)
            curtailment[['available','demand']].plot(ax=ax_twin,
                lw=4, fontsize=18, style={'available': 'g', 'demand': 'r'}, 
                alpha=0.7)

            curtailment.name = "%s - %s" % (zone, resource)
            return [curtailment, (ax, ax_twin), None]

    def _get_comp(self, resource):
        """Calculates time series of PG for one resource. 
        
        :param string resource: resource to consider.
        :return: time series of PG for selected resource and axis object \ 
            containing information to plot. 
        """

        fig = plt.figure(figsize=(20, 10))
        plt.title('%s' % resource.capitalize(), fontsize=22)
        
        first = True
        total = pd.DataFrame()
        for z in self.zones:
            PG, capacity = self._get_PG(z, [resource])
            if PG is None:
                pass
            else:
                ax = fig.gca()
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

        if total.empty:
            plt.close()
            return [None, (None, None), None]
        else:
            total.name = resource
            return [total, (ax, None), None]

    def get_plot(self):
        """Plots data.

        """
        for data in self.data:
            if data[0] is not None:
                ax = data[1]
                self._set_canvas(ax)

        plt.show()

    def get_data(self):
        """Returns data frame.

        """
        if self.kind == "stacked":
            data = np.array([d[0] for d in self.data])
        elif self.kind == "comp":
            data = np.reshape(self.data, (1, len(self.resources), 3))[:,:,0]
        elif self.kind == "curtailment":
            data = np.reshape(self.data,
                              (len(self.zones), len(self.resources), 3))[:,:,0]
        
        return data
