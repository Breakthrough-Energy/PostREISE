import { useState } from "react";

// Credit: https://www.telerik.com/blogs/better-modals-in-react
const useOpenClose = (startOpen = false) => {
  const [isOpen, setIsOpen] = useState(startOpen);

  const open = () => {
      setIsOpen(true);
  };

  const toggle = () => {
    setIsOpen(!isOpen);
  }

  const close = () => {
      setIsOpen(false);
  };

  return { isOpen, open, toggle, close };
};

export default useOpenClose;
