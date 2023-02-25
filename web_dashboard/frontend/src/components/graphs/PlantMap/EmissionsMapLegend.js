import React from 'react';
import classNames from 'classnames';
import { PLANT_COLOR_MODE } from '../../../hooks/graphs/usePlantLayer/usePlantLayer';
import PropTypes from 'prop-types';

import './EmissionsMapLegend.css';

const EmissionsMapLegend = ({ className, plantColorMode }) => {
  const cn = 'emissions-map-legend';

  let sections;
  if (plantColorMode === PLANT_COLOR_MODE.EMISSIONS_DIFF) {
    sections = [
      { text: <>Less tons CO<sub>2</sub></>, color: '#78D911' },
      { text: <>More tons CO<sub>2</sub></>, color: '#FF8563' }
    ];
  } else {
    sections = [
      { text: <>Coal: CO<sub>2</sub></>, color: '#000000' },
      { text: <>Natural Gas: CO<sub>2</sub></>, color: '#8B36FF' }
    ];
  }

  const renderSection = ({ text, color }) => {
    return (
      <div className={`${cn}__section`} key={color}>
        <div className={`${cn}__circle`} style={{ backgroundColor: color }} />
        {text}
      </div>
    );
  }

  return (
    <div className={classNames(className, cn)}>
      {sections.map(renderSection)}
    </div>
  );
};

EmissionsMapLegend.propTypes = {
  className: PropTypes.string,
  plantColorMode: PropTypes.string,
}

export default EmissionsMapLegend;
