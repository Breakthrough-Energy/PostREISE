import React from 'react';
import classNames from 'classnames';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

import { addColumn, changeScenario, removeColumn, updateFilter } from '../../../slices/dashboardSlice/dashboardSlice';
import GradientBorder from '../../common/GradientBorder/GradientBorder';
import Select from '../../common/Select/Select.js';
import {  SCENARIO_INFO,
          SCENARIO_LABEL,
          SCENARIO_LABEL_PLURAL,
          SCENARIO_ORDER_FOR_SELECT_COMPONENT,
          LOCATION_LABEL,
          MAX_COLUMNS } from '../../../data/scenario_info';
import { SHOW_ALL_TEXT, STATES } from '../../../data/states';

import '../../common/css/Variables.css';
import './ScenarioToolbar.css';

// These come from the store and get inserted into our props
const mapStateToProps = state => ({
  graphColumns: state.dashboardSlice.graphColumns,
  selectedLocation: state.dashboardSlice.filters.location
});
const dispatchProps = { addColumn, changeScenario, removeColumn, updateFilter };

export class ScenarioToolbar extends React.Component {
  onAddColumnClicked = () => {
    const { addColumn, graphColumns } = this.props;
    if (graphColumns.length < MAX_COLUMNS) {
      addColumn();
    }
  }

  handleSelectScenario = (graphColumnId, scenarioId) => {
    const { changeScenario, removeColumn } = this.props;
    if (scenarioId === 'removeColumn') {
      removeColumn({ graphColumnId });
    } else {
      changeScenario({ graphColumnId, scenarioId });
    }
  }

  renderInfoBox = paragraphList => {
    return (
      <div className='scenario-toolbar__infobox-description'>
        {paragraphList.map((paragraph) => <p key={uuidv4()}>{paragraph}</p>)}
      </div>
    );
  }

  renderScenarioSelector = graphColumn => {
    const canCloseColumns = this.props.graphColumns.length > 1;

    const optionData = SCENARIO_ORDER_FOR_SELECT_COMPONENT.reduce((optionDataAcc, scenarioId) => {
      // If we only have one column, don't include the option to close it
      if (scenarioId === 'removeColumn' && !canCloseColumns) {
        return optionDataAcc;
      } else {
        const { name, descList } = SCENARIO_INFO[scenarioId];
        optionDataAcc[scenarioId] = {
          text: name,
          infoBox: this.renderInfoBox(descList)
        };
        return optionDataAcc;
      }
    }, {});

    return (
      <Select
        className="scenario-toolbar__select"
        key={graphColumn.id}
        value={graphColumn.scenarioId}
        options={optionData}
        showInfoBox={true}
        onOptionClicked={this.handleSelectScenario.bind(this, graphColumn.id)} />
    );
  }

  handleSelectLocation = location => {
    this.props.updateFilter({ key: 'location', value: location });
  }

  render() {
    const { graphColumns, selectedLocation } = this.props;
    const addButtonClass = classNames(
      'scenario-toolbar__add',
      {'scenario-toolbar__add__disabled': graphColumns.length >= 3}
    );
    const scenarioLabel = graphColumns.length === 1
      ? `${SCENARIO_LABEL}:`
      : `${SCENARIO_LABEL_PLURAL}:`;

    const locationOptionData = Object.keys(STATES).reduce((optData, zone) => {
      optData[zone] = { text: zone }
      return optData
    }, { 'Show All': { text: SHOW_ALL_TEXT }});

    return (
      <header className="scenario-toolbar">
        <div className="scenario-toolbar__scenarios">
          <span className="scenario-toolbar__scenario-label">
            {scenarioLabel}
          </span>
          {graphColumns.map(this.renderScenarioSelector)}
          <button
            className={addButtonClass}
            onClick={this.onAddColumnClicked}>
            +
          </button>
          <span className="scenario-toolbar__location-label">
            {LOCATION_LABEL}:
          </span>
          <Select
            className="scenario-toolbar__location-select"
            value={selectedLocation}
            options={locationOptionData}
            onOptionClicked={this.handleSelectLocation} />
        </div>
        <GradientBorder />
      </header>
    );
  }
}

ScenarioToolbar.propTypes = {
  addColumn: PropTypes.func,
  changeScenario: PropTypes.func,
  graphColumns: PropTypes.array,
  removeColumn: PropTypes.func,
  selectedLocation: PropTypes.string,
  updateFilter: PropTypes.func,
}

export default connect(mapStateToProps, dispatchProps)(ScenarioToolbar);
