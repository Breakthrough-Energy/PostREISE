import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers
import numpy as np
import pandas as pd
import seaborn as sns


class AnalyzePG():
    """Manipulates PG.

    """

    def __init__(self, scenario, time, zones, resources, kind, normalize=False):
        """Constructor.

        :param tuple scenario: parameters related to scenario. 1st element \ 
            is a data frame of the power generated with id of the plants as \ 
            columns and UTC timestamp as indices. 2nd element is a grid \ 
            instance. 3rd element is an int indicating by which factor the \ 
            renewable energies have been increased. 
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

        self.PG = scenario[0].tz_localize('utc')
        self.grid = scenario[1]
        self.multiplier = scenario[2]

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

        if kind == 'stacked':
            self._do_stacked(time[0], time[1], time[2])
        elif kind == 'comp':
            self._do_comp(time[0], time[1], time[2])
        elif kind == 'curtailment':
            self._do_curtailment(time[0], time[1], time[2])
        elif kind == 'correlation':
            self._do_correlation(time[0], time[1], time[2])
        elif kind == 'chart':
            self._do_chart(time[0], time[1], time[2])
        elif kind == 'variability':
            self._do_variability(time[0], time[1], time[2])

    def _check_dates(self, start_date, end_date):
        """Test dates.

        :param string start_date: starting date
        :param string end_date: ending date
        """

        if pd.Timestamp(start_date) > pd.Timestamp(end_date):
            print("Starting date must be greater than ending date")
            raise Exception("Invalid dates")

    def _check_zones(self, zones):
        """Test zones.

        :param list zones: geographical zones.
        """
        all = list(self.grid.load_zones.values()) + ['California', 'Western']
        for z in zones:
            if z not in all:
                print("%s is incorrect. Possible zones are: %s" % (z, all))
                raise Exception('Invalid zone(s)')

    def _check_resources(self, resources):
        """Test resources.

        :param list resources: type of generators.
        """
        all = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']
        for r in resources:
            if r not in all:
                print("%s is incorrect. Possible resources are: %s" % (r, all))
                raise Exception('Invalid resource(s)')

    def _check_tz(self, tz):
        """Test time zone.

        :param string tz: time zone.
        """
        all = ['utc', 'US/Pacific', 'local']
        if tz not in all:
            print("%s is incorrect. Possible time zones are: %s" % (tz, all))
            raise Exception('Invalid time zone')

    def _check_freq(self, freq):
        """Test freq.

        :param string freq: frequency for resampling.
        """
        all = ['H', 'D', 'W', 'auto']
        if freq not in all:
            print("%s is incorrect. Possible frequency are: %s" % (freq, all))
            raise Exception('Invalid frequency')

    def _check_kind(self, kind):
        """Test kind.

        :param string kind: type of analysis.
        """
        all = ['chart', 'stacked', 'comp', 'curtailment', 'correlation', 
               'variability']
        if kind not in all:
            print("%s is incorrect. Possible analysis are: %s" % (kind, all))
            raise Exception('Invalid Analysis')

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

        first_available = self.PG.index[0].tz_convert(self.tz)
        last_available = self.PG.index[-1].tz_convert(self.tz)

        timestep = pd.DataFrame(index=pd.date_range(
            start_date, end_date, freq='H', tz=self.tz)).resample(
            self.freq, label='left').size().rename('Number of Hours')

        if self.freq == 'H':
            if first_available > pd.Timestamp(start_date, tz=self.tz):
                self.from_index = first_available
            else:
                self.from_index = pd.Timestamp(start_date, tz=self.tz)
            if last_available < pd.Timestamp(end_date, tz=self.tz):
                self.to_index = last_available
            else:
                self.to_index = pd.Timestamp(end_date, tz=self.tz)
        elif self.freq == 'D' or self.freq == 'W':
            if timestep[0] == timestep[1]:
                first_full = pd.Timestamp(timestep.index.values[0], tz=self.tz)
            else:
                first_full = pd.Timestamp(timestep.index.values[1], tz=self.tz)
            if timestep[-1] == timestep[-2]:
                last_full = pd.Timestamp(timestep.index.values[-1], tz=self.tz)
            else:
                last_full = pd.Timestamp(timestep.index.values[-2], tz=self.tz)

            if first_available > first_full:
                self.from_index = min(timestep[first_available:].index)
            else:
                self.from_index = first_full            
            if last_available < last_full:
                self.to_index = max(timestep[:last_available].index)
            else:
                self.to_index = last_full

        self.timestep = timestep[self.from_index:self.to_index]

    def _do_chart(self, start_date, end_date, tz):
        """ Do chart analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.
        """

        print('Set UTC for all zones')
        self.tz = 'utc'

        self._set_date_range(start_date, end_date)
        self.data = []
        self.filename = []
        for z in self.zones:
            self.data.append(self._get_chart(z))

    def _get_chart(self, zone):
        """Calculates proportion of resources for one zone.

        :param string zone: zone to consider.
        :return: numerical proportion of resources for the selected zone \ 
            along with axis object containing information to plot. 
        """

        PG, _ = self._get_PG(zone, self.resources)
        if PG is not None:
            fig, ax = plt.subplots(1, 2, figsize=(20, 10), sharey=True)
            plt.subplots_adjust(wspace=1)
            ax[0].set_title('Generation (MWh)', fontsize=25)
            ax[1].set_title('Resources (MW)', fontsize=25)
            
            PG_groups = PG.T.groupby(self.grid.genbus['type']).agg(sum).T
            PG_groups.name = "%s (Generation)" % zone
            #resources = PG_groups.columns
            type2label = self.type2label.copy()
            for type in self.grid.ID2type.values():
                if type not in PG_groups.columns:
                    del type2label[type]

            ax[0] = PG_groups.sum().plot(ax=ax[0], kind='barh', alpha=0.7,
                color=[self.grid.type2color[r] for r in type2label.keys()])

            capacity = self.grid.genbus.loc[PG.columns].groupby('type').agg(
                sum).GenMWMax.rename(index=type2label)
            capacity.name = "%s (Capacity)" % zone
            ax[1] = capacity.plot(ax=ax[1], kind='barh', alpha=0.7,
                color=[self.grid.type2color[r] for r in type2label.keys()])

            y_offset = 0.3
            for i in [0, 1]:
                ax[i].tick_params(axis='y', labelsize=20)
                ax[i].set_xticklabels('')
                ax[i].set_ylabel('')
                ax[i].spines['right'].set_visible(False)
                ax[i].spines['top'].set_visible(False)
                ax[i].spines['bottom'].set_visible(False)
                ax[i].set_xticks([])
                for p in ax[i].patches:
                    b = p.get_bbox()
                    val = format(int(b.x1), ',')
                    ax[i].annotate(val, (b.x1, b.y1-y_offset), fontsize=20)

            self.filename.append('%s_%s_%s-%s.png' % (
                self.kind, zone, self.from_index.strftime('%Y%m%d%H'),
                self.to_index.strftime('%Y%m%d%H')))

            return (PG_groups, capacity)
        else:
            return None

    def _do_stacked(self, start_date, end_date, tz):
        """Do stack analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.
        """

        self.data = []
        self.filename = []
        self.grid.read_demand_data()
        for z in self.zones:
            self.tz = self.zone2time[z] if tz == 'local' else tz
            self._set_date_range(start_date, end_date)
            self.data.append(self._get_stacked(z))

    def _get_stacked(self, zone):
        """Calculates time series of PG and demand for one zone. 

        :param string zone: zone to consider.
        :return: time series of PG and demand for selected zone along with \ 
            axis object containing information to plot. 
        """

        PG, capacity = self._get_PG(zone, self.resources)
        if PG is not None:
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s' % zone, fontsize=25)
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

            ax.grid(color='black', axis='y')
            ax.tick_params(labelsize=20)
            ax.set_xlabel('')
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], frameon=2,
                      prop={'size': 18}, loc='lower right')
            if self.normalize:
                ax.set_ylabel('Normalized Generation', fontsize=22)
            else:
                ax.set_ylabel('Generation (MWh)', fontsize=22)

            PG_stack['demand'] = demand
            PG_stack.name = zone

            self.filename.append('%s_%s_%s-%s.png' % (
                self.kind, zone, self.from_index.strftime('%Y%m%d%H'), 
                self.to_index.strftime('%Y%m%d%H')))

            return PG_stack
        else:
            return None

    def _do_comp(self, start_date, end_date, tz):
        """Do stack analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.
        """

        if tz == 'local':
            print('Set US/Pacific for all zones')
            self.tz = 'US/Pacific'
        else:
            self.tz = tz
        self._set_date_range(start_date, end_date)
        self.data = []
        self.filename = []
        for r in self.resources:
            self.data.append(self._get_comp(r))

    def _get_comp(self, resource):
        """Calculates time series of PG for one resource.

        :param string resource: resource to consider.
        :return: time series of PG for selected resource along with axis \ 
            object containing information to plot. 
        """

        fig = plt.figure(figsize=(20, 10))
        plt.title('%s' % resource.capitalize(), fontsize=25)

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

                ax.grid(color='black', axis='y')
                ax.tick_params(labelsize=20)
                ax.set_xlabel('')
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles[::-1], labels[::-1], frameon=2,
                          prop={'size': 18}, loc='lower right')
                if self.normalize:
                    ax.set_ylabel('Normalized Generation', fontsize=22)
                else:
                    ax.set_ylabel('Generation (MWh)', fontsize=22)
        if total.empty:
            plt.close()
            return None
        else:
            self.filename.append('%s_%s_%s_%s-%s.png' % (self.kind, resource,
                "-".join(self.zones), self.from_index.strftime('%Y%m%d%H'), 
                self.to_index.strftime('%Y%m%d%H')))
            total.name = resource
            return total

    def _do_curtailment(self, start_date, end_date, tz):
        """Do curtailment analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.
        """

        for r in self.resources:
            if r == 'solar':
                self.grid.read_solar_data()
            elif r == 'wind':
                self.grid.read_wind_data()
            else:
                print("Curtailment analysis is only for renewable energies")
                raise Exception('Invalid resource')

        self.data = []
        self.filename = []
        self.grid.read_demand_data()
        for z in self.zones:
            self.tz = self.zone2time[z] if tz == 'local' else tz
            self._set_date_range(start_date, end_date)
            for r in self.resources:
                self.data.append(self._get_curtailment(z, r))

    def _get_curtailment(self, zone, resource):
        """Calculates time series of curtailment for one zone and one resource.

        :param string zone: zone to consider.
        :param string resource: resource to consider.
        :return: time series of curtailment for selected zone along with \ 
            axis object containing information to plot.
        """

        PG, capacity = self._get_PG(zone, [resource])
        if PG is None:
            return None
        else:
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s (%s)' % (zone, resource.capitalize()), fontsize=25)
            ax = fig.gca()
            ax_twin = ax.twinx()

            demand = self._get_demand(zone)
            available = self._get_profile(zone, resource)

            curtailment = pd.DataFrame(available.T.sum().rename('available'))
            curtailment['generated'] = PG.T.sum().values
            curtailment['demand'] = demand.values

            multiplier = 1
            curtailment['available'] *= self.multiplier
            curtailment['ratio'] = 100 * \
                (1 - curtailment['generated'] / curtailment['available'])

            # Nnumerical precision
            curtailment.loc[abs(curtailment['ratio']) < 1, 'ratio'] = 0

            curtailment['ratio'].plot(ax=ax, legend=False, style='b', lw=4,
                alpha=0.7)
            curtailment[['available', 'demand']].plot(ax=ax_twin, lw=4,
                alpha=0.7, style={'available': 'g', 'demand': 'r'})

            ax.tick_params(labelsize=20)
            ax.grid(color='black', axis='y')
            ax.set_xlabel('')
            ax.set_ylabel('Curtailment [%]', fontsize=22)
            ax_twin.tick_params(labelsize=20)
            ax_twin.set_ylabel('MWh', fontsize=22)
            ax_twin.legend(loc='upper right', prop={'size': 18})

            curtailment.name = "%s - %s" % (zone, resource)
            
            self.filename.append('%s_%s_%s_%s-%s.png' % (self.kind, resource,
                zone, self.from_index.strftime('%Y%m%d%H'),
                self.to_index.strftime('%Y%m%d%H')))
            
            return curtailment

    def _do_variability(self, start_date, end_date, tz):
        """Do variability analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.
        """

        for r in self.resources:
            if r not in ['solar', 'wind']:
                print("Curtailment analysis is only for renewable energies")
                raise Exception('Invalid resource')

        self.data = []
        self.filename = []
        for z in self.zones:
            self.tz = self.zone2time[z] if tz == 'local' else tz
            self._set_date_range(start_date, end_date)
            for r in self.resources:
                self.data.append(self._get_variability(z, r))

    def _get_variability(self, zone, resource):
        """Calculates time series of PG for one zone and one resource. Also \
            calculates the time series of the PG of 2, 8 and 15 randomly \ 
            chosen plants in the same zone and using the same resource.

        :param string resource: resource to consider.
        :return: time series of PG for selected zone and selected plants \ 
            along with axis object containing information to plot.         
        """

        PG, capacity = self._get_PG(zone, [resource])
        if PG is None:
            return None
        else:
            n_plants = len(PG.columns)
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s (%s)' % (zone, resource.capitalize()), fontsize=25)
            ax = fig.gca()

            total = pd.DataFrame(PG.T.sum().rename(
                'Total: %d plants (%d MW)' % (n_plants, capacity)))
            total.name = "%s - %s" % (zone, resource)

            np.random.seed(10)
            if n_plants < 20:
                print("Not enough %s plants in %s for variability analysis" \
                      % (resource, zone))
                plt.close()
                return None
            else:
                selected = np.random.choice(PG.columns, 15, 
                                            replace=False).tolist()
                norm = [capacity]
                for i in [15, 8, 2]:
                    norm += [sum(self.grid.genbus.loc[
                        selected[:i]].GenMWMax.values)]
                total['15 plants (%d MW)' % norm[1]] = PG[selected].T.sum()
                total['8 plants (%d MW)' % norm[2]] = PG[selected[:8]].T.sum()
                total['2 plants (%d MW)' % norm[3]] = PG[selected[:2]].T.sum()

                if self.normalize:
                    for i, col in enumerate(total.columns):
                        total[col] = total[col].divide(
                            norm[i] * self.timestep, axis='index')

                lws = [5,3,3,3]
                lss = ['-','--','--','--']
                colors = [self.grid.type2color[resource]]
                if resource == 'solar':
                    colors += ['red','orangered','darkorange']
                elif resource == 'wind':
                    colors += ['dodgerblue','teal','turquoise']

                for col, c, lw, ls in zip(total.columns, colors, lws, lss):
                    total[col].plot(alpha=0.7, lw=lw, ls=ls, color= c, ax=ax)

                ax.grid(color='black', axis='y')
                ax.tick_params(labelsize=20)
                ax.set_xlabel('')
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles[::-1], labels[::-1], frameon=2,
                          prop={'size': 18}, loc='top right')
                if self.normalize:
                    ax.set_ylabel('Normalized Generation', fontsize=22)
                else:
                    ax.set_ylabel('Generation (MWh)', fontsize=22)

                self.filename.append('%s_%s_%s_%s-%s.png' % (self.kind, 
                    resource, zone, self.from_index.strftime('%Y%m%d%H'), 
                    self.to_index.strftime('%Y%m%d%H')))

                return total

    def _do_correlation(self, start_date, end_date, tz):
        """Do correlation analysis.

        :param string start_date: starting timestamp.
        :param string end_date: ending timestamp.
        :param string tz: timezone.        
        """

        for r in self.resources:
            if r not in ['solar', 'wind']:
                print("Correlation analysis is only for renewable energies")
                raise Exception('Invalid resource')

        if tz == 'local':
            print('Set US/Pacific for all zones')
            self.tz = 'US/Pacific'
        else:
            self.tz = tz
        self._set_date_range(start_date, end_date)
        self.data = []
        self.filename = []
        for r in self.resources:
            self.data.append(self._get_correlation(r))

    def _get_correlation(self, resource):
        """Calculates correlation coefficient of PG for one resource.

        :param string resource: resource to consider.
        :return: correlation coefficients of PG for selected resource as a \ 
            data frame along with an axis object containing information to plot.         
        """

        fig = plt.figure(figsize=(12, 12))
        plt.title('%s' % resource.capitalize(), fontsize=25)

        first = True
        PG = pd.DataFrame()
        for z in self.zones:
            PG_tmp, _ = self._get_PG(z, [resource])
            if PG_tmp is None:
                pass
            else:                
                if first:
                    PG = pd.DataFrame({z: PG_tmp.sum(axis=1).values}, 
                                      index=PG_tmp.index)
                    first = False
                else:
                    PG[z] = PG_tmp.sum(axis=1).values

        if PG.empty:
            plt.close()
            return None
        else:
            PG.name = resource
            corr = PG.corr()
            if resource == 'solar':
                palette = 'OrRd'
            elif resource == 'wind':
                palette = 'Greens'

            ax = fig.gca()
            ax = sns.heatmap(corr, annot=True, fmt=".2f", cmap=palette,
                             ax=ax, square=True, cbar=False, 
                             annot_kws={"size": 18}, lw=4)
            ax.set_yticklabels(PG.columns, rotation=40, ha='right')
            ax.tick_params(labelsize=20)

            pd.plotting.scatter_matrix(PG, alpha=0.2, diagonal='hist',
                                       figsize=(12,12))
            
            for type in ['matrix', 'scatter']:
                self.filename.append('%s-%s_%s_%s_%s-%s.png' % (
                    self.kind, type, resource, "-".join(self.zones),
                    self.from_index.strftime('%Y%m%d%H'), 
                    self.to_index.strftime('%Y%m%dH')))

            return PG

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

    def get_plot(self, save=False):
        """Plots data.

        """

        if save is True:
            figures = [manager.canvas.figure for manager in \
                       matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
            for i, f in enumerate(figures):
                f.savefig(self.filename[i], bbox_inches='tight', pad_inches=0)

        plt.show()

    def get_data(self):
        """Returns data frame.

        """
        if self.kind is "stacked":
            data = {}
            for i, z in enumerate(self.zones):
                data[z] = self.data[i]
        if self.kind is "chart":
            data = {}
            for i, z in enumerate(self.zones):
                data[z] = {}
                data[z]['Generation'] = self.data[i][0]
                data[z]['Capacity'] = self.data[i][1]
        elif self.kind is "comp" or self.kind is "correlation":
            data = {}
            for i, r in enumerate(self.resources):
                data[r] = self.data[i]
        elif self.kind is 'variability' or self.kind is "curtailment":
            data = {}
            index = 0
            for z in self.zones:
                data[z] = {}
                for r in self.resources:
                    data[z][r] = self.data[index]
                    index += 1

        return data
