import React from 'react';

import '../../../common/css/Variables.css';
import './UpgradedInterconnectionMapLegend.css';

const UpgradedInterconnectionMapLegend = () => {
  const cn = 'upgraded-interconnection-map-legend';
  return (
    <div className={cn}>
      <div className="flex-center"><div className={`${cn}__u`} />Connected Grid</div>
      <div className="flex-center"><div className={`${cn}__hvdc`} />HVDC</div>
    </div>
  );
};

export default UpgradedInterconnectionMapLegend;
