import { useRef, useEffect } from "react";

// used to store prevState or prevProps
// more info: https://blog.logrocket.com/how-to-get-previous-props-state-with-react-hooks/
const usePrevious = (value) => {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export default usePrevious;
