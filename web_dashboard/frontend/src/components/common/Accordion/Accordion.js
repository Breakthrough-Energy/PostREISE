import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import useOpenClose from '../../../hooks/useOpenClose/useOpenClose';

import './Accordion.css';

// This component can either manage its own state or be managed by a parent
// It renders its children even when closed and hides them with css display: none
// This is specifically for scrollytelling, where we need to avoid reloading bokeh graphs
const Accordion = ({ className, childClassName, isOpenOverride, toggleEl, onToggle, children }) => {
  const { isOpen, toggle } = useOpenClose(isOpenOverride);

  const showChild = isOpen || isOpenOverride;
  const accordionClass = classNames(className, 'accordion', { 'overflow-hidden': !showChild }, { 'overflow-visible': showChild });
  const childClass = classNames(childClassName, 'accordion__child', { 'animated-close': !showChild }, { 'animated-open': showChild });

  const onToggleClick = () => {
    if (isOpenOverride === null) {
      toggle();
    }
    if (onToggle) {
      onToggle(isOpen);
    }
  };

  return (
    <div className={accordionClass}>
      <div onClick={onToggleClick}>
        {toggleEl}
      </div>
      <div className={childClass}>
        {children}
      </div>
    </div>
  );
};

Accordion.propTypes = {
  className: PropTypes.string,
  childClassName: PropTypes.string,
  isOpenOverride: PropTypes.bool,
  toggleEl: PropTypes.node,
  onToggle: PropTypes.func,
  children: PropTypes.node
}

Accordion.defaultProps = {
  isOpenOverride: null,
  onToggle: null
}

export default Accordion;
