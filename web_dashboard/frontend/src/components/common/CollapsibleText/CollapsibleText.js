import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { LESS, MORE } from '../../../data/misc_text';
import Shiitake from 'shiitake';

import '../css/Variables.css';
import './CollapsibleText.css';

const CollapsibleText = ({ className, lines, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const canOpen = useRef(null);
  const fullClassName = `${className} collapsible-text`;

  const setCanOpen = (isTruncated) => {
    // Only set once
    if (canOpen.current === null) {
      canOpen.current = isTruncated
    }
  }

  const onClick = () => {
    if (canOpen.current) {
      setIsOpen(!isOpen);
    }
  }

  // If the text is open, return a regular div
  if (isOpen) {
    return (
      <div className={fullClassName + ' open'} onClick={onClick}>
        {children}
        <span className="collapsible-text__button">{LESS}</span>
      </div>
    );
  }

  // Else return a special collapsible component
  return (
    <Shiitake
      attributes={{ className: fullClassName, onClick }}
      lines={lines}
      onTruncationChange={setCanOpen}
      overflowNode={(
        <span>...<span className="collapsible-text__button">{MORE}</span></span>
      )}>
      {children}
    </Shiitake>
  );
}

CollapsibleText.propTypes = {
  className: PropTypes.string,
  lines: PropTypes.number,
  children: PropTypes.string
}

CollapsibleText.defaultProps = {
  lines: 2
}

export default CollapsibleText;
