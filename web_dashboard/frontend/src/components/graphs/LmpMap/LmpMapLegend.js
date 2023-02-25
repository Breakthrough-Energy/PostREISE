import React from 'react';
import classNames from 'classnames';

import './LmpMapLegend.css';

const LmpMapLegend = ({ className }) => {
  const cn = 'lmp-map-legend';
  const sections = [
    { tick: "25" },
    { tick: "30" },
    { tick: "35" },
    { tick: "40" },
    { tick: "45" },
  ];

  const renderSection = (section, index) => {
    let addLeftTick = (index === 0) ? true : false;
    return (
      <div className={`${cn}__section`} key={section.tick}>
        <div className={`${cn}__spacer`} />
        {addLeftTick && <div className={`${cn}__firstTick`}>{section.tick-5}</div>}
        <div className={`${cn}__tick`}>{section.tick}</div>
      </div>
    );
  }

  return (
    <div className={classNames(className, cn)}>
      <div className={`${cn}__title`}>Locational Marginal Prices ($/MWh)</div>
      <div className={`${cn}__sections`}>
        {sections.map(renderSection)}
      </div>
    </div>
  );
};

export default LmpMapLegend;