import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pandas.plotting import scatter_matrix

plt.ioff()


class AnalyzePG:
    """Analysis based on PG.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param tuple time: time related parameters. 1st element is the starting
        date. 2nd element is the ending date (left out). 3rd element is the
        timezone, only *'utc'*, *'US/Pacific'* and *'local'* are possible. 4th
        element is the frequency, which can be *'H'* (hour), *'D'* (day), *'W'*
         (week) or *'auto'*.
    :param list zones: geographical zones. Any combinations of load zones in the
        Western interconnection or ERCOT plus *'California'*, *'Western'* or
        *'Texas'*.
    :param list resources: energy resources. Can be any combinations of
        *'coal'*, *'dfo'*, *'geothermal'*, *'hydro'*, *'ng'*, *'nuclear'*,
        *'solar'*, *'wind'*.
    :param str kind: one of: *'stacked'*, *'comp'*, *'curtailment'*,
        *'correlation'*, *'chart'*, *'variability'* or *'yield'*.
    :param bool normalize: should generation be normalized by capacity.
    :param int seed: seed for random number generator. Only used in the
        *'variability'* analysis.

    .. note::
        * *'stacked'*:
            calculates time series of power generated and demand in one zone.
        * *'comp'*:
            calculates time series of power generated for one resource in
                multiple zones.
        * *'curtailment'*:
            calculates time series of curtailment for one resource in one zone.
        * *'correlation'*:
            calculates correlation coefficients of power generated between
                multiple zones for one resource.
        * *'chart'*:
            calculates proportion of resources and generation in one zone.
        * *'variability'*:
            calculates time series of power generated in one zone for one
            resource. Also calculates the time series of the power generated
            of 2, 8 and 15 randomly chosen plants in the same zone and using
            the same resource.
        * *'yield'*:
            calculates capacity factor of one resource in one zone.
    """

    def __init__(self, scenario, time, zones, resources, kind,
                 normalize=False, seed=0):
        """Constructor.

        """
        plt.close('all')

        # Note: Data is downloaded even if not needed
        self.pg = scenario.state.get_pg().tz_localize('utc')
        self.grid = scenario.state.get_grid()
        self.demand = scenario.state.get_demand(original=True)
        self.solar = scenario.state.get_solar()
        self.wind = scenario.state.get_wind()
        self.hydro = scenario.state.get_hydro()
        self.interconnect = self.grid.interconnect

        if self.grid.storage and 'storage' in resources:
            self.storage_pg = scenario.state.get_storage_pg().tz_localize('utc')
        else:
            self.storage_pg = None

        # Zone to time zone
        self.zone2time = {'Arizona': 'US/Mountain',
                          'Bay Area': 'US/Pacific',
                          'California': 'US/Pacific',
                          'Central California': 'US/Pacific',
                          'Colorado': 'US/Mountain',
                          'El Paso': 'US/Mountain',
                          'Idaho': 'US/Mountain',
                          'Montana Western': 'US/Mountain',
                          'Nevada': 'US/Mountain',
                          'New Mexico Western': 'US/Mountain',
                          'Northern California': 'US/Pacific',
                          'Oregon': 'US/Pacific',
                          'Southeast California': 'US/Pacific',
                          'Southwest California': 'US/Pacific',
                          'Utah': 'US/Mountain',
                          'Washington': 'US/Pacific',
                          'Western': 'US/Pacific',
                          'Wyoming': 'US/Mountain',
                          'Coast': 'US/Central',
                          'East': 'US/Central',
                          'Far West': 'US/Central',
                          'North': 'US/Central',
                          'North Central': 'US/Central',
                          'South': 'US/Central',
                          'South Central': 'US/Central',
                          'Texas': 'US/Central',
                          'West': 'US/Central',
                          'Eastern': 'US/Eastern'}

        # Fuel type to label for used in plots
        self.type2label = {'nuclear': 'Nuclear',
                           'geothermal': 'Geothermal',
                           'coal': 'Coal',
                           'dfo': 'Fuel Oil',
                           'hydro': 'Hydro',
                           'solar': 'Solar',
                           'wind': 'Wind',
                           'ng': 'Natural Gas',
                           'storage': 'Storage Discharging'}

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
        self.seed = seed

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
            self._do_chart(time[0], time[1])
        elif kind == 'variability':
            self._do_variability(time[0], time[1], time[2])
        elif kind == 'yield':
            self._do_yield(time[0], time[1])

    @staticmethod
    def _check_dates(start_date, end_date):
        """Test dates.

        :param str start_date: starting date.
        :param str end_date: ending date.
        :raise Exception: if dates are invalid.
        """
        if pd.Timestamp(start_date) > pd.Timestamp(end_date):
            print("Starting date must be greater than ending date")
            raise Exception("Invalid dates")

    def _check_zones(self, zones):
        """Test zones.

        :param list zones: geographical zones.
        :raise Exception: if zone(s) are invalid.
        """
        possible = list(self.grid.id2zone.values())
        if 'Western' in self.interconnect:
            possible += ['California', 'Western']
        if 'Texas' in self.interconnect:
            possible += ['Texas']
        if 'Eastern' in self.interconnect:
            possible += ['Eastern']
        for z in zones:
            if z not in possible:
                print("%s is incorrect. Possible zones are: %s" %
                      (z, possible))
                raise Exception('Invalid zone(s)')

    def _check_resources(self, resources):
        """Test resources.

        :param list resources: type of generators.
        :raise Exception: if resource(s) are invalid.
        """
        for r in resources:
            if r not in self.type2label.keys():
                print("%s is incorrect. Possible resources are: %s" %
                      (r, self.type2label.keys()))
                raise Exception('Invalid resource(s)')

    @staticmethod
    def _check_tz(tz):
        """Test time zone.

        :param str tz: time zone.
        :raise Exception: if time zone is invalid.
        """
        possible = ['utc', 'US/Pacific', 'local']
        if tz not in possible:
            print("%s is incorrect. Possible time zones are: %s" %
                  (tz, possible))
            raise Exception('Invalid time zone')

    @staticmethod
    def _check_freq(freq):
        """Test freq.

        :param str freq: frequency for re-sampling.
        :raise Exception: if frequency is invalid.
        """
        possible = ['H', 'D', 'W', 'auto']
        if freq not in possible:
            print("%s is incorrect. Possible frequency are: %s" %
                  (freq, possible))
            raise Exception('Invalid frequency')

    @staticmethod
    def _check_kind(kind):
        """Test kind.

        :param str kind: type of analysis.
        :raise Exception: if analysis is invalid.
        """
        possible = ['chart', 'stacked', 'comp', 'curtailment', 'correlation',
                    'variability', 'yield']
        if kind not in possible:
            print("%s is incorrect. Possible analysis are: %s" %
                  (kind, possible))
            raise Exception('Invalid Analysis')

    def _convert_tz(self, df_utc):
        """Convert data frame from UTC time zone to desired time zone.

        :param pandas.DataFrame df_utc: data frame with UTC timestamp as
            indices.
        :return: (*pandas.DataFrame*) -- data frame converted to desired
            time zone.
        """
        df_new = df_utc.tz_convert(self.tz)
        df_new.index.name = self.tz

        return df_new

    def _set_frequency(self, start_date, end_date):
        """Sets frequency for resampling.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        """
        delta = pd.Timestamp(start_date) - pd.Timestamp(end_date)

        if delta.days < 7:
            self.freq = 'H'
        elif 31 < delta.days < 180:
            self.freq = 'D'
        else:
            self.freq = 'W'

    def _set_date_range(self, start_date, end_date):
        """Calculates the appropriate date range after resampling in order to
            get an equal number of entries per sample.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        """
        first_available = self.pg.index[0].tz_convert(self.tz)
        last_available = self.pg.index[-1].tz_convert(self.tz)

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

        elif self.freq == 'D':
            if timestep[0] == timestep[1]:
                first_full = pd.Timestamp(timestep.index.values[0], tz=self.tz)
            else:
                first_full = pd.Timestamp(timestep.index.values[1], tz=self.tz)
            if timestep[-1] == timestep[-2]:
                last_full = pd.Timestamp(timestep.index.values[-1], tz=self.tz)
            else:
                last_full = pd.Timestamp(timestep.index.values[-2], tz=self.tz)

            if first_available > first_full:
                self.from_index = first_available.ceil('D')
            else:
                self.from_index = first_full
            if last_available < pd.Timestamp(end_date, tz=self.tz):
                self.to_index = last_available.floor('D') - \
                                pd.Timedelta('1 days')
            else:
                self.to_index = last_full

        elif self.freq == 'W':
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

    def _do_chart(self, start_date, end_date):
        """Performs chart analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        """
        print('Set UTC for all zones')
        self.tz = 'utc'

        self._set_date_range(start_date, end_date)
        self.data = []
        self.filename = []
        for z in self.zones:
            self.data.append(self._get_chart(z))

    def _get_chart(self, zone):
        """Calculates proportion of resources and generation in one zone.

        :param str zone: zone to consider.
        :return: (*tuple*) -- First element is a time series of PG with type of
            generators as columns. Second element is a data frame with type of
            generators as indices and corresponding capacity as column.
        """
        pg, _ = self._get_pg(zone, self.resources)
        if pg is not None:
            fig, ax = plt.subplots(1, 2, figsize=(20, 10), sharey='row')
            plt.subplots_adjust(wspace=1)
            plt.suptitle("%s" % zone, fontsize=30)
            ax[0].set_title('Generation (MWh)', fontsize=25)
            ax[1].set_title('Resources (MW)', fontsize=25)

            pg_groups = pg.T.groupby(self.grid.plant['type']).agg(sum).T
            pg_groups.name = "%s (Generation)" % zone
            type2label = self.type2label.copy()
            for t in self.grid.id2type.values():
                if t not in pg_groups.columns:
                    del type2label[t]

            ax[0] = pg_groups[list(type2label.keys())].rename(
                index=type2label).sum().plot(
                ax=ax[0], kind='barh', alpha=0.7,
                color=[self.grid.type2color[r] for r in type2label.keys()])

            capacity = self.grid.plant.loc[pg.columns].groupby(
               'type').agg(sum).GenMWMax
            capacity.name = "%s (Capacity)" % zone

            ax[1] = capacity[list(type2label.keys())].rename(
                index=type2label).plot(
                ax=ax[1], kind='barh', alpha=0.7,
                color=[self.grid.type2color[r] for r in type2label.keys()])

            y_offset = 0.3
            for i in [0, 1]:
                ax[i].tick_params(axis='y', which='both', labelsize=20)
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

            return pg_groups, capacity
        else:
            return None

    def _do_stacked(self, start_date, end_date, tz):
        """Performs stack analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        :param str tz: timezone.
        """
        self.data = []
        self.filename = []
        for z in self.zones:
            self.tz = self.zone2time[z] if tz == 'local' else tz
            self._set_date_range(start_date, end_date)
            self.data.append(self._get_stacked(z))

    def _get_stacked(self, zone):
        """Calculates time series of PG and demand in one zone. 

        :param str zone: zone to consider.
        :return: (*pandas.DataFrame*) --  data frame of PG and load for selected
            zone.
        """
        pg, capacity = self._get_pg(zone, self.resources)
        if pg is not None:

            demand = self._get_demand(zone)

            pg_groups = pg.T.groupby(self.grid.plant['type'])
            pg_stack = pg_groups.agg(sum).T

            if self.storage_pg is not None:
                pg_storage, capacity_storage = self._get_storage_pg(zone)
                if capacity_storage is not None:
                    capacity += capacity_storage
                    pg_stack = pd.merge(
                        pg_stack,
                        pg_storage.clip(lower=0).sum(axis=1).rename('storage'),
                        left_index=True,
                        right_index=True)
                    fig, (ax, ax_storage) = plt.subplots(
                        2, 1, figsize=(20, 15), sharex='row',
                        gridspec_kw={'height_ratios': [3, 1], 'hspace': 0})
                    plt.subplots_adjust(wspace=0)
                    ax_storage = pg_storage.tz_localize(None).sum(
                        axis=1).rename('batteries').plot(
                        color=self.grid.type2color['storage'], lw=4,
                        ax=ax_storage)
                    ax_storage.fill_between(
                        pg_storage.tz_localize(None).index.values, 0,
                        pg_storage.tz_localize(None).sum(axis=1).values,
                        color=self.grid.type2color['storage'], alpha=0.5)

                    ax_storage.tick_params(axis='both', which='both',
                                           labelsize=20)
                    ax_storage.set_xlabel('')
                    ax_storage.set_ylabel('Energy Storage (MW)', fontsize=22)
                    for a in fig.get_axes():
                        a.label_outer()
                else:
                    fig = plt.figure(figsize=(20, 10))
                    ax = fig.gca()
            else:
                fig = plt.figure(figsize=(20, 10))
                ax = fig.gca()

            type2label = self.type2label.copy()
            for t in self.grid.id2type.values():
                if t not in pg_stack.columns:
                    del type2label[t]

            net_demand = pd.DataFrame({'net_demand': demand['demand']},
                                      index=demand.index)
            for t in type2label.keys():
                if t == 'solar' or t == 'wind':
                    net_demand['net_demand'] = net_demand['net_demand'] - \
                                               self._get_pg(zone,
                                                            [t])[0].sum(axis=1)

            if self.normalize:
                pg_stack = pg_stack.divide(capacity * self.timestep,
                                           axis='index')
                demand = demand.divide(capacity * self.timestep, axis='index')
                net_demand = net_demand.divide(capacity * self.timestep,
                                               axis='index')
                ax.set_ylabel('Normalized Generation', fontsize=22)
            else:
                pg_stack = pg_stack.divide(1000, axis='index')
                demand = demand.divide(1000, axis='index')
                net_demand = net_demand.divide(1000, axis='index')
                ax.set_ylabel('Generation (GW)', fontsize=22)

            ax = pg_stack[list(type2label.keys())].tz_localize(None).rename(
                columns=type2label).plot.area(
                color=[self.grid.type2color[r] for r in type2label.keys()], 
                alpha=0.7, ax=ax)
            demand.tz_localize(None).plot(color='red', lw=4, ax=ax)
            net_demand.tz_localize(None).plot(color='red', ls='--', lw=2, ax=ax)
            ax.set_ylim([min(0, net_demand['net_demand'].min()),
                         max(ax.get_ylim()[1], 1.1*demand.max().values[0])])

            ax.set_title('%s' % zone, fontsize=25)
            ax.grid(color='black', axis='y')
            ax.tick_params(which='both', labelsize=20)
            ax.set_xlabel('')
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], frameon=2,
                      prop={'size': 18}, loc='lower right')

            pg_stack['demand'] = demand
            pg_stack.name = zone

            self.filename.append('%s_%s_%s-%s.png' % (
                self.kind, zone, self.from_index.strftime('%Y%m%d%H'), 
                self.to_index.strftime('%Y%m%d%H')))

            return pg_stack
        else:
            return None

    def _do_comp(self, start_date, end_date, tz):
        """Performs comparison analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        :param str tz: timezone.
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

        :param str resource: resource to consider.
        :return: (*pandas.DataFrame*) -- data frame of PG for selected resource.
        """
        fig = plt.figure(figsize=(20, 10))
        plt.title('%s' % resource.capitalize(), fontsize=25)

        first = True
        total = pd.DataFrame()
        for z in self.zones:
            pg, capacity = self._get_pg(z, [resource])
            if pg is None:
                pass
            else:
                ax = fig.gca()
                col_name = '%s: %d plants (%d MW)' % (z, pg.shape[1], capacity)
                total_tmp = pd.DataFrame(pg.T.sum().rename(col_name))

                if self.normalize:
                    total_tmp = total_tmp.divide(capacity * self.timestep,
                                                 axis='index')
                if first:
                    total = total_tmp
                    first = False
                else:
                    total = pd.merge(total, total_tmp, left_index=True,
                                     right_index=True)

                total[col_name].tz_localize(None).plot(lw=4, alpha=0.8, ax=ax)

                ax.grid(color='black', axis='y')
                ax.tick_params(which='both', labelsize=20)
                ax.set_xlabel('')
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles[::-1], labels[::-1], frameon=2,
                          prop={'size': 18})
                if self.normalize:
                    ax.set_ylabel('Normalized Generation', fontsize=22)
                else:
                    ax.set_ylabel('Generation (MWh)', fontsize=22)
        if total.empty:
            plt.close()
            return None
        else:
            self.filename.append('%s_%s_%s_%s-%s.png' %
                                 (self.kind, resource, "-".join(self.zones),
                                  self.from_index.strftime('%Y%m%d%H'),
                                  self.to_index.strftime('%Y%m%d%H')))
            total.name = resource
            return total

    def _do_curtailment(self, start_date, end_date, tz):
        """Performs curtailment analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        :param str tz: timezone.
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
                self.data.append(self._get_curtailment(z, r))

    def _get_curtailment(self, zone, resource):
        """Calculates time series of curtailment for one resource in one zone.

        :param str zone: zone to consider.
        :param str resource: resource to consider.
        :return: (*pandas.DataFrame*) -- data frame of curtailment for selected
            zone and resource. Columns are energy available (in MWh) from
            generators using resource in zone, energy generated (in MWh) from
            generators using resource in zone, demand in selected zone (in MWh)
            and curtailment (in %).
        """
        pg, capacity = self._get_pg(zone, [resource])
        if pg is None:
            return None
        else:
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s (%s)' % (zone, resource.capitalize()), fontsize=25)
            ax = fig.gca()
            ax_twin = ax.twinx()

            demand = self._get_demand(zone)
            available = self._get_profile(zone, resource)

            data = pd.DataFrame(available.T.sum().rename('available'))
            data['generated'] = pg.T.sum().values
            data['demand'] = demand.values
            data['curtailment'] = (1 - data['generated'] / data['available'])
            data['curtailment'] *= 100

            # Numerical precision
            data.loc[abs(data['curtailment']) < 1, 'curtailment'] = 0

            data['curtailment'].tz_localize(None).plot(ax=ax, style='b', lw=4,
                                                       alpha=0.7)
            data['available'].tz_localize(
                None).rename("%s energy available" % resource).plot(
                ax=ax_twin, lw=4, alpha=0.7, style={
                    "%s energy available" % resource: self.grid.type2color[
                        resource]})
            data['demand'].tz_localize(None).plot(ax=ax_twin, lw=4, alpha=0.7,
                                                  style={'demand': 'r'})
            ax.tick_params(which='both', labelsize=20)
            ax.grid(color='black', axis='y')
            ax.set_xlabel('')
            ax.set_ylabel('Curtailment [%]', fontsize=22)
            ax.legend(loc='upper left', prop={'size': 18})
            ax_twin.tick_params(which='both', labelsize=20)
            ax_twin.set_ylabel('MWh', fontsize=22)
            ax_twin.legend(loc='upper right', prop={'size': 18})

            data.name = "%s - %s" % (zone, resource)

            self.filename.append('%s_%s_%s_%s-%s.png' %
                                 (self.kind, resource,
                                  zone, self.from_index.strftime('%Y%m%d%H'),
                                  self.to_index.strftime('%Y%m%d%H')))

            return data

    def _do_variability(self, start_date, end_date, tz):
        """Performs variability analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        :param str tz: timezone.
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
        """Calculates time series of PG in one zone for one resource. Also,
            calculates the time series of the PG of 2, 8 and 15 randomly
            chosen plants in the same zone and using the same resource.

        :param str resource: resource to consider.
        :return: (*pandas.DataFrame*) -- data frame of PG for selected zone and
            plants.
        """
        pg, capacity = self._get_pg(zone, [resource])
        if pg is None:
            return None
        else:
            n_plants = len(pg.columns)
            fig = plt.figure(figsize=(20, 10))
            plt.title('%s (%s)' % (zone, resource.capitalize()), fontsize=25)
            ax = fig.gca()

            total = pd.DataFrame(pg.T.sum().rename(
                'Total: %d plants (%d MW)' % (n_plants, capacity)))
            total.name = "%s - %s" % (zone, resource)

            np.random.seed(self.seed)
            if n_plants < 20:
                print("Not enough %s plants in %s for variability analysis"
                      % (resource, zone))
                plt.close()
                return None
            else:
                selected = np.random.choice(pg.columns, 15,
                                            replace=False).tolist()
                norm = [capacity]
                for i in [15, 8, 2]:
                    norm += [sum(self.grid.plant.loc[
                        selected[:i]].GenMWMax.values)]
                total['15 plants (%d MW)' % norm[1]] = pg[selected].T.sum()
                total['8 plants (%d MW)' % norm[2]] = pg[selected[:8]].T.sum()
                total['2 plants (%d MW)' % norm[3]] = pg[selected[:2]].T.sum()

                if self.normalize:
                    for i, col in enumerate(total.columns):
                        total[col] = total[col].divide(
                            norm[i] * self.timestep, axis='index')

                lws = [5, 3, 3, 3]
                lss = ['-', '--', '--', '--']
                colors = [self.grid.type2color[resource]]
                if resource == 'solar':
                    colors += ['red', 'orangered', 'darkorange']
                elif resource == 'wind':
                    colors += ['dodgerblue', 'teal', 'turquoise']

                for col, c, lw, ls in zip(total.columns, colors, lws, lss):
                    total[col].tz_localize(None).plot(alpha=0.7, lw=lw, ls=ls,
                                                      color=c, ax=ax)

                ax.grid(color='black', axis='y')
                ax.tick_params(which='both', labelsize=20)
                ax.set_xlabel('')
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles[::-1], labels[::-1], frameon=2,
                          prop={'size': 18}, loc='best')
                if self.normalize:
                    ax.set_ylabel('Normalized Generation', fontsize=22)
                else:
                    ax.set_ylabel('Generation (MWh)', fontsize=22)

                self.filename.append('%s_%s_%s_%s-%s.png' %
                                     (self.kind,
                                      resource, zone,
                                      self.from_index.strftime('%Y%m%d%H'),
                                      self.to_index.strftime('%Y%m%d%H')))

                return total

    def _do_correlation(self, start_date, end_date, tz):
        """Performs correlation analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        :param str tz: timezone.
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
        """Calculates correlation coefficients of power generated between
            multiple zones for one resource.

        :param str resource: resource to consider.
        :return: (*pandas.DataFrame*) -- data frame of PG for selected resource.
            Columns are zones for selected resource.
        """

        fig = plt.figure(figsize=(12, 12))
        plt.title('%s' % resource.capitalize(), fontsize=25)

        first = True
        pg = pd.DataFrame()
        for z in self.zones:
            pg_tmp, _ = self._get_pg(z, [resource])
            if pg_tmp is None:
                pass
            else:
                if first:
                    pg = pd.DataFrame({z: pg_tmp.sum(axis=1).values},
                                      index=pg_tmp.index)
                    first = False
                else:
                    pg[z] = pg_tmp.sum(axis=1).values

        if pg.empty:
            plt.close()
            return None
        else:
            pg.name = resource
            corr = pg.corr()
            if resource == 'solar':
                palette = 'OrRd'
                color = 'red'
            else:
                palette = 'Greens'
                color = 'green'

            ax_matrix = fig.gca()
            ax_matrix = sns.heatmap(corr, annot=True, fmt=".2f", cmap=palette,
                                    ax=ax_matrix, square=True, cbar=False,
                                    annot_kws={"size": 18}, lw=4)
            ax_matrix.set_yticklabels(pg.columns, rotation=40, ha='right')
            ax_matrix.tick_params(which='both', labelsize=20)

            scatter = scatter_matrix(pg, alpha=0.2, diagonal='kde',
                                     figsize=(12, 12), color=color,
                                     density_kwds={'color': color, 'lw': 4})
            for ax_scatter in scatter.ravel():
                ax_scatter.tick_params(labelsize=20)
                ax_scatter.set_xlabel(ax_scatter.get_xlabel(), fontsize=22,
                                      rotation=0)
                ax_scatter.set_ylabel(ax_scatter.get_ylabel(), fontsize=22,
                                      rotation=90)

            for t in ['matrix', 'scatter']:
                self.filename.append('%s-%s_%s_%s_%s-%s.png' %
                                     (self.kind, t, resource,
                                      "-".join(self.zones),
                                      self.from_index.strftime('%Y%m%d%H'),
                                      self.to_index.strftime('%Y%m%dH')))

            return pg

    def _do_yield(self, start_date, end_date):
        """Performs yield analysis.

        :param str start_date: starting timestamp.
        :param str end_date: ending timestamp.
        """

        for r in self.resources:
            if r not in ['solar', 'wind']:
                print("Correlation analysis is only for renewable energies")
                raise Exception('Invalid resource')

        self.tz = 'utc'
        self.data = []
        self.filename = []
        for z in self.zones:
            self._set_date_range(start_date, end_date)
            for r in self.resources:
                self.data.append(self._get_yield(z, r))

    def _get_yield(self, zone, resource):
        """Calculates capacity factor of one resource in one zone.

        :param str zone: zone to consider.
        :param str resource: resource to consider.
        :return: (*tuple*) -- first element is the average ideal capacity
            factor for the selected zone and resource. Second element is the
            average curtailed capacity factor for the selected zone and
            resource.
        """

        pg, _ = self._get_pg(zone, [resource])
        if pg is None:
            return None
        else:
            available = self._get_profile(zone, resource)

            capacity = self.grid.plant.loc[pg.columns].GenMWMax.values

            uncurtailed = available.sum().divide(len(pg) * capacity,
                                                 axis='index')
            mean_uncurtailed = np.mean(uncurtailed)
            curtailed = pg.sum().divide(len(pg) * capacity, axis='index')
            mean_curtailed = np.mean(curtailed)

            if len(pg.columns) > 10:
                fig = plt.figure(figsize=(12, 12))
                plt.title('%s (%s)' % (zone, resource.capitalize()),
                          fontsize=25)
                ax = fig.gca()
                cf = pd.DataFrame({'uncurtailed': 100 * uncurtailed,
                                   'curtailed': 100 * curtailed},
                                  index=pg.columns)
                cf.boxplot(ax=ax)
                plt.text(0.5, 0.9, '%d plants' % len(capacity), ha='center',
                         va='center', transform=ax.transAxes, fontsize=22)
                ax.tick_params(labelsize=20)
                ax.set_ylabel('Capacity Factor [%]', fontsize=22)

                self.filename.append('%s_%s_%s_%s-%s.png' %
                                     (self.kind, resource, zone,
                                      self.from_index.strftime('%Y%m%d%H'),
                                      self.to_index.strftime('%Y%m%d%H')))

            return mean_uncurtailed, mean_curtailed

    def _get_zone_id(self, zone):
        """Returns the load zone identification numbers for specified zone.

        :param zone: zone to consider. A specific load zone, *Eastern*,
            *Western*, *California* or *Texas*.
        :return (*list*): Corresponding load zones identification number.
        """
        if zone == 'Western':
            load_zone_id = list(range(201, 217))
        elif zone == 'Texas':
            load_zone_id = list(range(301, 309))
        elif zone == 'California':
            load_zone_id = list(range(203, 208))
        elif zone == 'Eastern':
            load_zone_id = list(range(1, 53))
        else:
            load_zone_id = [self.grid.zone2id[zone]]

        return load_zone_id

    def _get_plant_id(self, zone, resource):
        """Extracts the plant identification number of all the generators
            located in one zone and using one specific resource.

        :param str zone: zone to consider.
        :param str resource: type of generator to consider.
        :return: (*list*) -- plant id of all the generators located in zone and
            using resource.
        """
        plant_id = []
        for z in self._get_zone_id(zone):
            try:
                plant_id += self.grid.plant.groupby(
                    ['zone_id', 'type']).get_group(
                    (z, resource)).index.values.tolist()
            except KeyError:
                pass

        return plant_id

    def _get_pg(self, zone, resources):
        """Returns PG of all the generators located in one zone and powered by
            resources.

        :param str zone: one of the zones.
        :param list resources: type of generators to consider.
        :return: (*tuple*) -- data frames of PG and associated capacity for all
            generators located in zone and using the specified resources.
        """
        plant_id = []
        for r in resources:
            plant_id += self._get_plant_id(zone, r)

        if len(plant_id) == 0:
            print("No %s plants in %s" % ("/".join(resources), zone))
            return [None] * 2
        else:
            capacity = sum(self.grid.plant.loc[plant_id].GenMWMax.values)
            pg = self._convert_tz(self.pg[plant_id]).resample(
                self.freq, label='left').sum()[self.from_index:self.to_index]

            return pg, capacity

    def _get_storage_pg(self, zone):
        """Returns PG of all storage units located in zone

        :param str zone: one of the zones
        :return: (*tuple*) -- date frame of PG and associated capacity for all
            storage units located in zone.
        """
        storage_id = []
        for c, bus in enumerate(self.grid.storage['gen'].bus_id.values):
            if self.grid.bus.loc[bus].zone_id in self._get_zone_id(zone):
                storage_id.append(c)

        if len(storage_id) == 0:
            print("No storage units in %s" % zone)
            return [None] * 2
        else:
            capacity = sum(self.grid.storage['gen'].loc[storage_id].Pmax.values)
            pg = self._convert_tz(self.storage_pg[storage_id]).resample(
                self.freq, label='left').sum()[self.from_index:self.to_index]

            return pg, capacity

    def _get_demand(self, zone):
        """Returns demand profile for a specific load zone, *Eastern*,
            *Western*, *California* or *Texas*.

        :param str zone: one of the zones.
        :return: (*pandas.DataFrame*) -- data frame of demand in zone (in MWh).
        """
        demand = self.demand.tz_localize('utc')
        demand = demand[self._get_zone_id(zone)].sum(axis=1).rename(
            'demand').to_frame()
        demand = self._convert_tz(demand).resample(
            self.freq, label='left').sum()[self.from_index:self.to_index]

        return demand

    def _get_profile(self, zone, resource):
        """Returns profile for resource.

        :param str zone: zone to consider.
        :param str resource: type of generators to consider.
        :return: (*pandas.DataFrame*) -- data frame of the generated energy (in
            MWh) in zone by generators using resource.
        """
        plant_id = self._get_plant_id(zone, resource)

        if len(plant_id) == 0:
            print("No %s plants in %s" % (resource, zone))
            return None

        profile = eval('self.'+resource).tz_localize('utc')

        return self._convert_tz(profile[plant_id]).resample(
            self.freq, label='left').sum()[self.from_index:self.to_index]

    def get_plot(self, save=False):
        """Plots analysis.

        :param bool save: should plot be saved.
        """
        if save:
            for i in plt.get_fignums():
                plt.figure(i)
                plt.savefig(self.filename[i-1], bbox_inches='tight',
                            pad_inches=0)
        plt.show()

    def get_data(self):
        """Get data.

        :return: (*dict*) -- the formatting of the data depends on the selected
            analysis.
            
        .. note::
            * *'stacked'*:
                1D dictionary. Keys are zones and associated value is a data
                frame.
            * *'chart'*:
                2D dictionary. First key is zone and associated value is a
                dictionary, which has *'Generation'* and *'Capacity'* as keys
                and a data frame for value.
            *  *'comp'* and *'correlation'*:
                1D dictionary. Keys are resources and associated value is a
                data frame.
            *  *'variability'*, *'curtailment'* and *'yield'*:
                2D dictionary. First key is zone and associated value is a
                dictionary, which has resources as keys and a data frame for
                value.
 
        """
        data = None
        if self.kind == "stacked":
            data = {}
            for i, z in enumerate(self.zones):
                data[z] = self.data[i]
        elif self.kind == "chart":
            data = {}
            for i, z in enumerate(self.zones):
                data[z] = {}
                data[z]['Generation'] = self.data[i][0]
                data[z]['Capacity'] = self.data[i][1]
        elif self.kind == "comp" or self.kind == "correlation":
            data = {}
            for i, r in enumerate(self.resources):
                data[r] = self.data[i]
        elif self.kind == 'variability' or self.kind == "curtailment" or \
                self.kind == 'yield':
            data = {}
            index = 0
            for z in self.zones:
                data[z] = {}
                for r in self.resources:
                    data[z][r] = self.data[index]
                    index += 1

        return data
