import React, { Fragment } from 'react';
import { connect } from 'react-redux';

import DashboardGraph from '../DashboardGraph/DashboardGraph';
import { IoMdClose } from 'react-icons/io';
import { removeColumn } from '../../../slices/dashboardSlice/dashboardSlice';

import { SCENARIO_INFO } from '../../../data/scenario_info';

import '../../common/css/Variables.css';
import './GraphColumn.css';

// These come from the store and get inserted into our props
const mapStateToProps = (state, { id }) => {
  const graphColumn = state.dashboardSlice.graphColumns.find(col => col.id === id);
  const canClose = state.dashboardSlice.graphColumns.length > 1;
  return { canClose: canClose, scenarioId: graphColumn.scenarioId, graphs: graphColumn.graphs };
};
const dispatchProps = { removeColumn };

export const GraphColumn = ({ id, canClose, graphs, scenarioId, removeColumn }) => {
  const onCloseClicked = () => removeColumn({ graphColumnId: id });

  const renderGraphWrapper = graph => {
    // This is a special case where we skip offshore wind if a scenario does
    // not have data for it
    // TODO: this should be handled in the store
    // where a new column should be created each time we switch the scenario
    const hasOffshoreWind = SCENARIO_INFO[scenarioId].offshoreWind;
    if (graph.graphType === 'offshoreWindCurtailment' && !hasOffshoreWind) {
      return null;
    }

    return (
      <DashboardGraph
        key={graph.id}
        id={graph.id}
        scenarioId={scenarioId}
        graphType={graph.graphType} />
    );
  }

  return (
    <Fragment>
      <div className="graph-column__grid-item graph-column__column-header">
        <h1 className="graph-column__scenario-name">
          {SCENARIO_INFO[scenarioId]['name']}
        </h1>
        {SCENARIO_INFO[scenarioId].descList.map((para, i) =>
          <p key={i} className="graph-column__scenario-subtitle">{para}</p>
        )}
        {canClose
          && <IoMdClose className='graph-column__close' onClick={onCloseClicked}/>
        }
      </div>
      <div className='graph-column__grid-item graph-column__graph-list'>
        {graphs.map(renderGraphWrapper)}
      </div>
    </Fragment>
  );
};

export default connect(mapStateToProps, dispatchProps)(GraphColumn);
