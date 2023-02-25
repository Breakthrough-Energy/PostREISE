import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';

import './EllipsisText.css';

const EllipsisText = (props) => {
  const wrapperClass = classNames('ellipsisWrapper', props.className);

  return (
    <div {...props} className={wrapperClass} >
      <div className="ellipsisWrapper__ellipsis">
        {props.children}
      </div>
    </div>
  );
}

EllipsisText.propTypes = {
  className: PropTypes.string,
  children: PropTypes.string
}

export default EllipsisText;
