import React, {useState} from 'react';

import DeckGL from '@deck.gl/react';
import {LineLayer} from '@deck.gl/layers';
import RangeInput from './HourlySlider';

import { load } from '@loaders.gl/core';
import { JSONLoader } from '@loaders.gl/json';
import * as aq from 'arquero';
import { scaleThreshold } from 'd3-scale';

import ButtonGroup from '../common/ButtonGroup/ButtonGroup';

import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import * as moment from 'moment-timezone'

import {styled} from '@material-ui/core/styles';
import './HourlyUtilization.css';

const INITIAL_VIEW_STATE = {
  latitude: 37.09024,
  longitude: -95.712891,
  zoom: 3.7,
  pitch: 0,
  bearing: 0
};

const S_PER_HOUR = 3.6e3;
const S_PER_DAY = S_PER_HOUR * 24;
// const NUM_DAYS_IN_RANGE = 7;
const NUM_DAYS_IN_RANGE = 6*30;
const MAX_DATA_CHUNKS = 14;

function formatLabel(t) {
  if (isNaN(t)){ return "" }
  const date = moment.unix(t);
  return `${date.tz("America/Chicago").format('dddd, L, LT')}`;
}

function formatDayLabel(t) {
  if (isNaN(t)){ return "" }
  const date = moment.unix(t);
  return `${date.tz("America/Chicago").format('dddd, L')}`;
}

function getTimeRange(objects) {
  if (!objects) {
    return null;
  }
  const times = Object.keys(objects)
                      .map(Number)
                      .filter(d => !Number.isNaN(d))
  const timeRange = times.reduce(
    (range, d) => {
      range[0] = Math.min(range[0], d);
      range[1] = Math.max(range[1], d);
      return range;
    },
    [Infinity, -Infinity]
  );
  return [timeRange[0], timeRange[1]]
}

// Used in branch maps
export const createTrafficScale = (min, max) => {
  const increment = (max-min) / 5;
  const domain = []
  for (let i = 0; i < 5; i++) {
    domain.push(min + increment * i);
  }

  return scaleThreshold()
    .domain(domain)
    .range([
      [189,189,189,200], // gray
      [27, 150, 66],  // green
      [166, 218, 106],  // lightgreen
      [247, 247, 41], // yellow
      [252, 174, 97],  // orange
      [214, 33, 29], // red
    ]);
}

const trafficScale = createTrafficScale(0, 1);

const PositionContainer = styled('div')({
  position: 'absolute',
  zIndex: 1,
  top: '10px',
  width: '100%',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center'
});

function getRangeDays(weekStart) {
  const days = [weekStart];
  for (let i = 1; i < NUM_DAYS_IN_RANGE; i += 1) {
    days.push(
      moment(weekStart)
        .add(i, 'days')
    );
  }
  return days;
}

const HourlyUtilization = () => {
  const [sliderValue, setSliderValue] = useState('yearMedian');
  const [timeRange, setTimeRange] = useState();
  const [dataNotLoaded, setNotDataLoaded] = useState(true);
  const [startDay, setStartDay] = React.useState(1);
  const [selectedDays, setSelectedDays] = React.useState(
    [moment("2016-01-01", 'YYYY-MM-DD'), moment("2016-01-07", 'YYYY-MM-DD')]);
  const [toggleIdx, setToggleIdx] = useState(0);

  const modifiers = { start: selectedDays[0], end: selectedDays[selectedDays.length-1] };

  const handleDayChange = (selectedDay) => {
    const days = getRangeDays(selectedDay);
    setSelectedDays(days);
  };

  function getTooltip({object}) {
    return (
      object &&
      `Branch ${object.branch_id}: ${object.capacity} MW, ${Math.round(object.median_utilization[sliderValue] * 100)}% Utilization`
    );
  }

  const checkDateBounds = timeRange => {
    const dataDateStart = moment.unix(timeRange[0]);
    const selectedDateStart = selectedDays[0];
    if (selectedDateStart.isAfter(dataDateStart)){
      timeRange[0] = selectedDateStart.unix();
    }

    const dataDateEnd = moment.unix(timeRange[1]);
    const selectedDateEnd = selectedDays[selectedDays.length-1];
    console.log(selectedDateEnd)
    console.log(dataDateEnd)
    console.log(selectedDateEnd.isBefore(dataDateEnd))
    console.log(selectedDateEnd.isAfter(dataDateEnd))
    if (selectedDateEnd.isAfter(dataDateEnd)){
      timeRange[1] = selectedDateEnd.unix();
    }

    return timeRange
  }

  const addUtilization = (newData, oldData) => {
    if (oldData.length === 0){
      return newData
    }
    if (newData.length === 0 && oldData.length > 0){
      return oldData
    }
    else{
      const t0 = performance.now();
      oldData.forEach((val, ind) => {
        val.median_utilization = Object.assign(val.median_utilization, newData[ind]);
        newData[ind] = val;
      })
      const t1 = performance.now();
      console.log(`Adding daily chunk of utilization took ${t1 - t0} milliseconds.`);
      let timeRange = getTimeRange(newData[0].median_utilization);
      timeRange = checkDateBounds(timeRange);
      setTimeRange(timeRange);
      return newData
    }
  }

  const getColors = data => {
    return trafficScale(data.median_utilization[sliderValue])
  }

  const handleToggle = idx => {
    console.log(idx)
    setToggleIdx(idx)
    setNotDataLoaded(true)
  }

  const setDate = date_str => {
    const date = moment(date_str)
    // setStartDay(date.dayOfYear())
    setStartDay(date.month() + 1)
    console.log(date.dayOfYear())
    setNotDataLoaded(true)
  }
  
  const branchLayer = new LineLayer({
    id: 'branch-layer',
    data: getData(startDay, toggleIdx, dataNotLoaded, setNotDataLoaded),
    dataTransform: addUtilization,
    pickable: true,
    widthScale: 5,
    widthMinPixels: 0.2,
    widthMaxPixels: 50,
    widthUnits: 'meters',
    getWidth: data => data.capacity,
    getSourcePosition: data => data.coords[0],
    getTargetPosition: data => data.coords[1],
    getColor: getColors,
    updateTriggers: {
      getColor: [ sliderValue, dataNotLoaded ],
    },
  });

  return (
    <>
      <PositionContainer>
        <label>Date Range (UTC): </label>
        <DayPickerInput
          value={selectedDays[0].toDate()}
          onDayChange={handleDayChange}
          dayPickerProps={{
            className: "Selectable",
            selectedDays: selectedDays,
            modifiers: modifiers,
            onDayClick: setDate,
          }}
        />
        —
        <DayPickerInput
          value={selectedDays[selectedDays.length-1].toDate()}
          onDayChange={handleDayChange}
          dayPickerProps={{
            className: "Selectable",
            selectedDays: selectedDays,
            modifiers: modifiers,
            onDayClick: setDate,
          }}
        />
        <ButtonGroup
          className="dashboard-graph__toggle"
          buttonClassName="dashboard-graph__toggle-button"
          items={["daily", "hourly"]}
          activeIdx={toggleIdx}
          onItemClick={handleToggle} 
        />
      </PositionContainer>
      <DeckGL
        layers={[branchLayer]}
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        getTooltip={getTooltip}
      >
      </DeckGL>

      {timeRange && (
        <RangeInput
          min={timeRange[0]}
          max={timeRange[1]}
          value={(!isNaN(sliderValue) ? sliderValue: timeRange[0])}
          animationSpeed={toggleIdx === 0? S_PER_DAY: S_PER_HOUR}
          formatLabel={toggleIdx === 0?formatDayLabel:formatLabel}
          onChange={setSliderValue}
        />
      )}
    </>
  );
}

async function* getData(startDay, toggleIdx, dataNotLoaded, setNotDataLoaded) {
  if (!dataNotLoaded) return;
  setNotDataLoaded(false);
  
  yield getBaseJson()
  for (let i = 1; i <= MAX_DATA_CHUNKS; i++) {
    yield getArrowFile(i, startDay, toggleIdx);
  }
}

const getBaseJson = async () => {
  const yearFile = "https://bescienceswebsite.blob.core.windows.net/grid-data/v1/1270/branch.json"
  console.log(yearFile)
  const yearly_chunk = await load(yearFile, JSONLoader);
  yearly_chunk.forEach(val => val.median_utilization = {'yearMedian': val.median_utilization});
  return yearly_chunk;
}

const getArrowFile = async (i, startDay, toggleIdx) => {
  var arrowFile;
  // if (toggleIdx === 0){
    arrowFile = `./arrow_data_files/util${i + (startDay-1)}.arrow`;
  // }
  // else{
  //   arrowFile = `https://cleanenergy.blob.core.windows.net/misc/hourly/util${i + (startDay-1)}.arrow.gz`;
  // }
  
  console.log(arrowFile)
  const util = await aq.loadArrow(arrowFile);
  const convertColumnToInt = aq.names(
    util.columnNames().map(x => moment(`${x.replace(/\s/, 'T')}Z`).unix())
                      .map(x => x.toString())
  )
  const chunk = util.rename(convertColumnToInt).objects();
  return chunk;
}

export default HourlyUtilization;