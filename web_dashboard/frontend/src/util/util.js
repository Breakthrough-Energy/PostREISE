import ReactGA from 'react-ga';
import { DESKTOP_BREAKPOINT } from '../data/constants';
import { INTERCONNECTIONS } from '../data/states';

/* Utility functions. Please break this file into modules when it gets big */

export const isDesktop = () => {
  return document.documentElement.clientWidth >= DESKTOP_BREAKPOINT;
};

export const HEADER_HEIGHT_DESKTOP = 93;
export const HEADER_HEIGHT_MOBILE = 52;

export const getHeaderHeight = () => {
  return isDesktop() ? HEADER_HEIGHT_DESKTOP : HEADER_HEIGHT_MOBILE;
}

// Rounds number to the nearest 2nd decimal place and localizes it with commas
export const numToDisplayString = (num, round=0) => {
  return num.toLocaleString(undefined, { minimumFractionDigits: round, maximumFractionDigits: round });
}

export const locationName2fileName = location => {
  if (location === null || location === 'Show All') return 'USA';
  else if (location in INTERCONNECTIONS) return INTERCONNECTIONS[location];
  return location;
}

// given a route, set Google Analytics pageview tracking
export const setPageTracking = (path) => {
  ReactGA.set({ page: path });
  ReactGA.pageview(path);
};

/** Find items that are missing from either array. Imagine a venn diagram.
  str whichDiff: "left", "right", or "both"
  func getKey(): creates a key for each item in the array
    e.g. if an array item is { id: 3, generation: 235 },
    getKey() might be x => x['id']
  NOTE: this was performance tested against two other methods of diffing arrays
  Method 1: leftArr.filter(x => rightArr.includes(x)) was 98.7% slower
  Method 2: leftArr.filter(x => rightSet.has(x)) was 21.7% slower
  TODO: In the future this can be replaced with Arquero by using an outer join on two tables
*/
export const getArrayDiff = (leftArr, rightArr, whichDiff="both", getKey=x=>x) => {
  const leftObj = {};
  const rightObj = {};
  let leftDiff = [];
  let rightDiff = [];

  if (whichDiff === "left" || whichDiff === "both") {
    // Turn rightArr into an object
    rightArr.forEach(val => rightObj[getKey(val)] = val);
    // Get items in leftArr that are not in rightArr
    leftDiff = leftArr.filter(val => !(rightObj.hasOwnProperty(getKey(val))));
  }

  if (whichDiff === "right" || whichDiff === "both") {
    // Turn leftArr into an object
    leftArr.forEach(val => leftObj[getKey(val)] = val);
    // Get items in rightArr that are not in leftArr
    rightDiff = rightArr.filter(val => !(leftObj.hasOwnProperty(getKey(val))));
  }

  return { leftDiff, leftObj, rightDiff, rightObj };
};
