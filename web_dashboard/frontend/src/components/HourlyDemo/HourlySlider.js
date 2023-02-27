import React, {useEffect, useState} from 'react';
import {styled, withStyles} from '@material-ui/core/styles';
import Slider from '@material-ui/core/Slider';
import Button from '@material-ui/core/IconButton';
import PlayIcon from '@material-ui/icons/PlayArrow';
import PauseIcon from '@material-ui/icons/Pause';

// const S_PER_HOUR = 3.6e3;

const PositionContainer = styled('div')({
  position: 'absolute',
  zIndex: 1,
  bottom: '40px',
  width: '100%',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center'
});

const SliderInput = withStyles({
  root: {
    marginLeft: 12,
    width: '80%'
  },
  valueLabel: {
    '& span': {
      background: 'none',
      color: '#000'
    }
  }
})(Slider);

export default function RangeInput({min, max, value, animationSpeed, onChange, formatLabel}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [animation] = useState({});

  // prettier-ignore
  useEffect(() => {
    return () => animation.id && cancelAnimationFrame(animation.id);
  }, [animation]);

  if (isPlaying && !animation.id) {
    let nextValue = value + animationSpeed;
    if (nextValue >= max) {
      nextValue = min;
    }
    animation.id = requestAnimationFrame(() => {
      animation.id = 0;
      onChange(nextValue);
    });
  }

  const isButtonEnabled = true;

  return (
    <PositionContainer>
      <Button color="primary" disabled={!isButtonEnabled} onClick={() => setIsPlaying(!isPlaying)}>
        {isPlaying ? <PauseIcon title="Stop" /> : <PlayIcon title="Animate" />}
      </Button>
      <SliderInput
        min={min}
        max={max}
        step={animationSpeed}
        marks
        value={value}
        onChange={(event, newValue) => onChange(newValue)}
        valueLabelDisplay="auto"
        valueLabelFormat={formatLabel}
      />
    </PositionContainer>
  );
}
