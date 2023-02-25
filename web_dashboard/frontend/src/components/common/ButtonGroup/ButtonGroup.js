import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';

import '../css/Variables.css';
import './ButtonGroup.css';

const ButtonGroup = ({ className, buttonClassName, items, activeIdx, onItemClick }) => {
  const buttonGroupClass = classNames(className, 'button-group');

  const renderButton = (item, i) => {
    const cn = classNames(
      buttonClassName,
      'button-group__button',
      { 'button-group__active': i === activeIdx }
    );

    return <div key={i} className={cn} onClick={onItemClick.bind(this, i)}>{item}</div>;
  }

  return (
    <div className={buttonGroupClass}>
      {items.map(renderButton)}
    </div>
  )
};

ButtonGroup.propTypes = {
  className: PropTypes.string,
  buttonClassName: PropTypes.string,
  items: PropTypes.arrayOf(PropTypes.node),
  activeIdx: PropTypes.number,
  onItemClick: PropTypes.func
}
export default ButtonGroup;
