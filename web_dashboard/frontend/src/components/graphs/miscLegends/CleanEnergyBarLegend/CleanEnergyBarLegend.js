import React from 'react';

import './CleanEnergyBarLegend.css';

const CleanEnergyBarLegend = () => {
  const cn = 'clean-energy-bar-legend';
  return (
    <div className={cn}>
      <div className={`${cn}__title`}>Clean Energy Sources:</div>
      <div className="flex-center"><div className={`${cn}__square ${cn}__0`} />Variable: Wind, Solar</div>
      <div className="flex-center"><div className={`${cn}__square ${cn}__1`} />Firm: Hydroelectric, Nuclear, Geothermal, Other</div>
    </div>
  );
};

export default CleanEnergyBarLegend;
