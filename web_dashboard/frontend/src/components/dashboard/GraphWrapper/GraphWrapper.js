import React from 'react';
import CanFullscreen from '../../common/CanFullscreen/CanFullscreen';
import CollapsibleText from '../../common/CollapsibleText/CollapsibleText';

import '../../common/css/Variables.css';
import './GraphWrapper.css';

// Handles visuals for showing graphs on the dashboard
const GraphWrapper = ({ title, controls, graph, subtitle }) => {
  return (
    <div className="graph">
      <CanFullscreen
        className="graph__fs-wrapper"
        fsClassName="graph__fullscreen"
        buttonClassName="graph__fullscreen-button">
        <div className="graph__title">{title}</div>
        <div className="graph__controls">
          {controls}
        </div>
        <div className="graph__content">
          {graph}
        </div>
        {subtitle
          &&  <div className="graph__subtitle">
                <CollapsibleText className="graph__ct">
                  {subtitle}
                </CollapsibleText>
              </div>}
      </CanFullscreen>
    </div>
  );
}

export default GraphWrapper;
