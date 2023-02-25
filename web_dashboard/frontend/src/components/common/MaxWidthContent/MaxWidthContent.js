import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';

import './MaxWidthContent.css';

// enum
export const ALIGN = {
  LEFT: 'left',
  CENTER: 'center',
  RIGHT: 'right',
};

const MaxWidthContent = ({ className, childClassName, maxWidth, mobileMaxWidth, align, mobileAlign, children }) => {
  let alignClass = `max-width-content__${align}`;
  let mobileAlignClass = mobileAlign ? `max-width-content__mobile__${mobileAlign}` : null;

  const wrapperClass = classNames(className, 'max-width-content__wrapper', alignClass, mobileAlignClass);
  const childClass = classNames(childClassName, 'max-width-content__child')
  const childStyle = {
    '--mwc-max-width': maxWidth,
    '--mwc-max-width-mobile': mobileMaxWidth
  };

  return (
    <div className={wrapperClass}>
      <div className={childClass} style={childStyle}>
        {children}
      </div>
    </div>
  );
}

MaxWidthContent.propTypes = {
  className: PropTypes.string,
  childClassName: PropTypes.string,
  maxWidth: PropTypes.string,
  mobileMaxWidth: PropTypes.string,
  align: PropTypes.string,
  mobileAlign: PropTypes.string,
  children: PropTypes.node
}

MaxWidthContent.defaultProps = {
  align: ALIGN.CENTER
}

export default MaxWidthContent;
