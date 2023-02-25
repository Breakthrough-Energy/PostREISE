import React from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { CARBON_FOOTNOTE } from '../../../data/graph_info';
import GraphColumn from '../GraphColumn/GraphColumn';
import Header from '../../Header/Header';
import ScenarioToolbar from '../ScenarioToolbar/ScenarioToolbar';
import { SECURITY_NOTICE } from '../../../data/scenario_info';

import '../../common/css/Variables.css';
import './Dashboard.css';

// These come from the store and get inserted into our props
const mapStateToProps = state => ({ graphColumns: state.dashboardSlice.graphColumns });

export const Dashboard = ({ graphColumns }) => {
  return (
    <div className="dashboard">
      <Header className="dashboard__header" />
      <ScenarioToolbar />
      <div className="dashboard__graph__grid">
        {graphColumns.map(graphColumn =>
          <GraphColumn key={graphColumn.id} id={graphColumn.id} />
        )}
      </div>
      <div className="dashboard__footer">
        {CARBON_FOOTNOTE}
        {SECURITY_NOTICE}
      </div>
    </div>
  );
};

Dashboard.propTypes = {
  graphColumns: PropTypes.array
}
export default connect(mapStateToProps)(Dashboard);
