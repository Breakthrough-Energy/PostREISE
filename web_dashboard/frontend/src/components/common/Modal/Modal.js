import React from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';
import PropTypes from 'prop-types';

import '../css/Variables.css';
import './Modal.css';

/**
 * Credit: https://www.telerik.com/blogs/better-modals-in-react
 * Multiple components may use this component at once
 * #modal-root will simply display multiple modal children
 * The parent must manage open / close state.
 * Note: The fullscreen param does not style the modal root as that element is
 * persistent outside of the modal component.
 *
 * Simple example:

  const { isOpen, open, close } = useOpenClose();

  return (
    <div>
      <button onClick={open}>Open</button>
      {isOpen && (
        <Modal className="foo__modal">
          <h1>This is a Modal using Portals!</h1>
          <button onClick={close}>OK</button>
        </Modal>)}
    </div>
  );
 */
const Modal = ({ className, children, fullscreen }) => {
  let modalRoot = document.getElementById('modal-root');

  if (!modalRoot) {
    modalRoot = document.createElement('div');
    modalRoot.setAttribute('id', 'modal-root');
    document.body.appendChild(modalRoot);
  }

  const modalClass = classNames('modal', className);
  let modalElement = <div className={modalClass}>{children}</div>;

  if (fullscreen) {
    // Wrap in a fullscreen div
    modalElement = <div className="modal__fullscreen">{modalElement}</div>;
  }

  return ReactDOM.createPortal(modalElement, modalRoot);
};

Modal.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node,
  fullscreen: PropTypes.string
}

export default Modal;
