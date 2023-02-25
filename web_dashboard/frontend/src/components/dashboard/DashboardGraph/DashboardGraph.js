import React, { useState } from 'react';
import { connect } from 'react-redux';

// Local imports
import ButtonGroup from '../../common/ButtonGroup/ButtonGroup';
import { GRAPH_INFO,
         NO_GRAPH_TEXT } from '../../../data/graph_info';
import { PLANT_COLOR_MODE } from '../../../hooks/graphs/usePlantLayer/usePlantLayer';
import { updateFilter } from '../../../slices/dashboardSlice/dashboardSlice';

// Graphs
import BranchMap from '../../graphs/BranchMap/BranchMap';
import CurtailmentLine from '../../graphs/CurtailmentLine/CurtailmentLine';
import GenerationBar from '../../graphs/GenerationBar/GenerationBar';
import GenerationPie from '../../graphs/GenerationPie/GenerationPie';
import GenerationStackedLine from '../../graphs/GenerationStackedLine/GenerationStackedLine';
import GraphWrapper from '../GraphWrapper/GraphWrapper';
import LmpMap from '../../graphs/LmpMap/LmpMap';
import PlantMap from '../../graphs/PlantMap/PlantMap';
import { PRESENT_DAY_SCENARIO } from '../../../data/scenario_info';

import './DashboardGraph.css';

const mapStateToProps = state => ({
  locationFilter: state.dashboardSlice.filters.location
});
const dispatchProps = { updateFilter };

// Handles logic for selecting the graph and any controls on the dashboard
export const DashboardGraph = ({ id, scenarioId, locationFilter, updateFilter, graphType }) => {
  // Determine if we can toggle other graphs
  // Currently the only graph that can toggle is 'allTransmission'
  const { toggleGraphs, toggleText } = GRAPH_INFO[graphType];
  const canToggleGraphs = toggleGraphs && toggleText;
  const [ toggleIdx, setToggleIdx ] = useState(0);

  const currentGraphType = canToggleGraphs ? toggleGraphs[toggleIdx] : graphType;

  // Get graph component
  const scenarioIdInt = scenarioId.substring(1); // s87 -> 87
  const presentDayScenarioIdInt = PRESENT_DAY_SCENARIO.substring(1);

  const setLocation = location => updateFilter({ key: 'location', value: location });

  const branchMap = <BranchMap scenarioId={scenarioIdInt} colorMode={canToggleGraphs && toggleText[toggleIdx]} location={locationFilter} setLocation={setLocation} />;

  const graphComponents = {
    // All scenarios show present day emissions graph
    'emissions': <PlantMap scenarioId={presentDayScenarioIdInt} colorMode={PLANT_COLOR_MODE.EMISSIONS} location={locationFilter} setLocation={setLocation} />,
    'emissionsDiff': <PlantMap scenarioId={scenarioIdInt} scenarioId2={presentDayScenarioIdInt} colorMode={PLANT_COLOR_MODE.EMISSIONS_DIFF} location={locationFilter} setLocation={setLocation} />,
    'genStack': <GenerationStackedLine scenarioId={scenarioIdInt} location={locationFilter} />,
    'lmp': <LmpMap scenarioId={scenarioIdInt} location={locationFilter} setLocation={setLocation} />,
    'genBar': <GenerationBar scenarioId={scenarioIdInt} location={locationFilter} />,
    'genPie': <GenerationPie scenarioId={scenarioIdInt} location={locationFilter} />,
    'transmissionUtilization': branchMap,
    'transmissionRisk': branchMap,
    'transmissionBind': branchMap,
    'windCurtailment': <CurtailmentLine scenarioId={scenarioIdInt} location={locationFilter} resourceType="wind" />,
    'offshoreWindCurtailment': <CurtailmentLine scenarioId={scenarioIdInt} location={locationFilter} resourceType="wind_offshore" />,
    'solarCurtailment': <CurtailmentLine scenarioId={scenarioIdInt} location={locationFilter} resourceType="solar" />,
  };

  const graph = graphComponents[currentGraphType] || <div>{NO_GRAPH_TEXT}</div>;

  const { title, subtitle, getTitle } = GRAPH_INFO[currentGraphType];

  // If these get more complicated they can be broken out into a separate component
  const controls = canToggleGraphs &&
    <ButtonGroup
      className="dashboard-graph__toggle"
      buttonClassName="dashboard-graph__toggle-button"
      items={toggleText}
      activeIdx={toggleIdx}
      onItemClick={idx => setToggleIdx(idx)} />

  return (
    <GraphWrapper
      title={title || getTitle(scenarioId)}
      controls={controls}
      graph={graph}
      subtitle={subtitle} />
  );
}

export default connect(mapStateToProps, dispatchProps)(DashboardGraph);
