import React from 'react';
import useOpenClose from './useOpenClose';

const MockOpenCloseComponent = () => {
  const { isOpen, open, toggle, close } = useOpenClose();

  return (
    <div>
      <p>{isOpen ? "OPENED" : "CLOSED"}</p>
      <button className="open" onClick={open}>Open</button>
      <button className="toggle" onClick={toggle}>Toggle</button>
      <button className="close" onClick={close}>Close</button>
    </div>
  );
}

export default MockOpenCloseComponent;
