import React from 'react';
import classNames from 'classnames';
import { numToDisplayString } from '../../../util/util';
import PropTypes from 'prop-types';

import './BranchMapLegend.css';

const BranchMapLegend = ({ className, title, min, max, unit }) => {
  const cn = 'branch-map-legend';

  const sectionsColors = [
    "#1b9642",
    "#a6da6a",
    "#f7f729",
    "#fcae61",
    "#d6211d"
  ];

  const renderSection = (color, i) => {
    // Calculate the value of the current tick
    // we render the first tick seperately, so we start index 1
    const increment = (max-min) / 5;
    const tickVal = min + increment * (i + 1);

    return (
      <div className={`${cn}__section`} key={tickVal}>
        {i === 0 && <div className={`${cn}__first-tick`}>{min}</div> }
        <div className={`${cn}__color`} style={{ backgroundColor: color }} />
        <div className={`${cn}__tick`}>{numToDisplayString(tickVal)}{unit}</div>
      </div>
    );
  }

  return (
    <div className={classNames(className, cn)}>
      <div className={`${cn}__title`}>{title}</div>
      <div className={`${cn}__sections`}>
        {sectionsColors.map(renderSection)}
      </div>
    </div>
  );
};

BranchMapLegend.propTypes = {
  className: PropTypes.string,
  title: PropTypes.string,
  min: PropTypes.number,
  max: PropTypes.number,
  unit: PropTypes.string
}

export default BranchMapLegend;
