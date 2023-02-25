import React, { useEffect } from 'react';

import classNames from 'classnames';
import PropTypes from 'prop-types';
import useOpenClose from '../../../hooks/useOpenClose/useOpenClose';
import { MdFullscreen } from 'react-icons/md';
import { MdFullscreenExit } from 'react-icons/md';
import Modal from '../Modal/Modal';

import '../css/Helpers.css';
import '../css/Variables.css';
import './CanFullscreen.css';

// fsChildren shows different content when in fullscreen
const CanFullscreen = ({ className, fsClassName, buttonClassName, children, fsChildren }) => {
  const { isOpen, toggle } = useOpenClose();
  const isOpenClasses = { 'can-fullscreen__fullscreen': isOpen };
  isOpenClasses[fsClassName] = isOpen
  const fullscreenClass = classNames('can-fullscreen', className, isOpenClasses)
  const buttonClass = classNames('can-fullscreen__button',  'reset-button-styles', buttonClassName);

  useEffect(() => {
    // We frequently use this with bokeh graphs, so we're including some
    // specialty code here. This fixes a bug where bokeh does not recognize
    // that it needs to update.
    setTimeout(() => window.dispatchEvent(new Event('resize')));
  }, [isOpen]);

  const childAndWrapper = (
    <div className={fullscreenClass}>
      {isOpen && fsChildren
        ? fsChildren
        : children
      }
      <button className={buttonClass}>
        {isOpen
          ? <MdFullscreenExit onClick={toggle}/>
          : <MdFullscreen onClick={toggle}/> }
      </button>
    </div>
  );

  return isOpen ? <Modal className="can-fullscreen__modal" fullscreen>{childAndWrapper}</Modal> : childAndWrapper;
}

CanFullscreen.propTypes = {
  className: PropTypes.string,
  buttonClassName: PropTypes.string,
  children: PropTypes.node
}

export default CanFullscreen;
