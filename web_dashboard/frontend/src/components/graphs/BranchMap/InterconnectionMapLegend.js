import React from 'react';

import '../../common/css/Variables.css';
import './InterconnectionMapLegend.css';

const InterconnectionMapLegend = () => {
  const cn = 'interconnection-map-legend';
  return (
    <div className={cn}>
      <div className="flex-center"><div className={`${cn}__w`} />Western</div>
      <div className="flex-center"><div className={`${cn}__e`} />Eastern</div>
      <div className="flex-center"><div className={`${cn}__t`} />Texas</div>
      <div className="flex-center"><div className={`${cn}__hvdc`} />HVDC</div>
    </div>
  );
};

export default InterconnectionMapLegend;
