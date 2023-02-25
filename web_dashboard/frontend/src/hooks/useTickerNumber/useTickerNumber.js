import { useEffect, useRef, useState } from 'react';
import usePrevious from '../usePrevious/usePrevious';

// REMEMBER TO CALL CLEANUP FUNCTION IN COMPONENT
// time to transition is in ms
const useNumberTicker = (initialNum, timeToTransition = 1000) => {
  const [number, setNumber] = useState(initialNum);
  const [targetNumber, setTargetNumber] = useState(initialNum);
  const prevTargetNumber = usePrevious(targetNumber)
  let setNumberTimeouts = useRef([]);

  const createSetNumberTimeout = (newNumber, delay, incrementDelay) => {
    const timeout = setTimeout(setNumber.bind(this, newNumber), delay)
    setNumberTimeouts.current.push(timeout);
  }

  const clearTimeouts = () => {
    setNumberTimeouts.current.forEach(timeout => {
      clearTimeout(timeout);
    });
    setNumberTimeouts.current = [];
  };

  // cleanup timers on unmount
  useEffect(() => clearTimeouts, [])

  useEffect(() => {
    if (targetNumber === prevTargetNumber) {
      return;
    }

    // TODO check targetNumber type is int or float
    // Cancel old timeouts
    clearTimeouts(setNumberTimeouts);

    // Space renders evenly within transition time
    const incrementDelay = timeToTransition/Math.abs(targetNumber - number);
    let totalDelay = 0;

    if (number > targetNumber) {
      for (let i = number + 1; i >= targetNumber; i--) {
        createSetNumberTimeout(i, totalDelay, incrementDelay);
        totalDelay += incrementDelay;
      }
    } else if (number < targetNumber) {
      for (let i = number - 1; i <= targetNumber; i++) {
        createSetNumberTimeout(i, totalDelay, incrementDelay);
        totalDelay += incrementDelay;
      }
    }
});

  return {
    'number': number,
    'setNumber': setTargetNumber
  }
}

export default useNumberTicker;
