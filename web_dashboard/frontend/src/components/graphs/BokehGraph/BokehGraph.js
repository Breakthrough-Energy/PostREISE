import Axios from 'axios';
import React, { useState, useEffect, useRef } from 'react';
import usePrevious from '../../../hooks/usePrevious/usePrevious';

const BokehGraph = ({ mapURI, mapRange, graphId, getPlotRef }) => {
  const prevMapURI = usePrevious(mapURI)
  const graphIndex = useRef(graphId);
  const targetId = useRef();
  const [isBokehRendered, setIsBokehRendered] = useState(false);
  const plotRef = useRef();
  const originalMapRangeRef = useRef();

  useEffect(() => {
    if (mapURI === prevMapURI) {
      return;
    }

    const source = Axios.CancelToken.source()
    Axios.get(mapURI)
        .then(resp => parseRespInfo(resp))
        .then(resp => displayBokehPlot(resp))
        .then(resp => waitForBokehModel(resp))
        .then(resp => getMapInfo(resp))
        .catch(resp => console.log(resp));

    const parseRespInfo = resp => {
      if (resp && resp.data && resp.data.root_id){
        const root_id = resp.data.root_id;

        // assign the map uuid as the root reference in the JSON graph document
        resp.data.root_id = graphId;
        resp.data.doc.roots.root_ids[0] = graphId;
        let root_ref = resp.data.doc.roots.references.find(x => x.id === root_id);
        root_ref.id = graphId;
      }
      else{
        console.log('root_id not defined...');
      }

      if (resp.data.target_id){
        targetId.current = resp.data.target_id;
      }
      else{
        console.log('target_id not defined...');
      }

      return resp;
    }

    // There was also an issue with Bokeh window.Bokeh.embed.embed_item function
    // not having a return value: bokeh/bokeh#9524
    // So within the Axios promise, this embed function kicks off and the promise
    // immediately continues executing following then blocks which find the graph
    // properties not rendered yet. The solution for now is to add an asynchronous
    // timeout that checks for the presence of rendered model every 100ms.
    const displayBokehPlot = resp => {
      try{
        if (isBokehRendered && graphId){
          window.Bokeh.index[graphId].model.document.replace_with_json(resp.data.doc);
        }
        else{
          window.Bokeh.embed.embed_item(resp.data, graphId);
        }
        // remove empty document entries
        window.Bokeh.documents = window.Bokeh.documents.filter(x => Object.keys(x._all_models).length !== 0)
      }
      catch(err) {
        console.log(err.message);
      }
      return resp;
    }

    // checks to see if the Bokeh map is available within the Bokeh virtual DOM
    const waitForBokehModel = async resp => {
      let i = 1;
      // error timeout of ~10 seconds
      while (typeof getPlotRef(graphId) !== 'object'){
        i++;
        if (i > 100) break;
        await wait(100);
      }
      return resp;
    };

    const getMapInfo = resp => {
      const plot = getPlotRef(graphId);
      if (typeof plot === 'object') {
        plotRef.current = plot;
      }
      else{
        console.log(`Could not get plot references for ${targetId.current} at index ${graphIndex.current}`)
      }

      // Save the original mapRange if we don't have it yet
      if (!originalMapRangeRef.current) {
        try{
          originalMapRangeRef.current = {
            xStart: plot.x_range.start,
            xEnd: plot.x_range.end,
            yStart: plot.y_range.start,
            yEnd: plot.y_range.end
          }
        }
        catch{
          console.log(`Could not get initial map range for ${targetId.current} at index ${graphIndex.current}`)
        }
      }

      setIsBokehRendered(true);

      if (mapRange){
        try{
          updateMap(plot, mapRange);
        }
        catch{
          console.log(`Could not set range for ${targetId.current} at index ${graphIndex.current}`);
        }
      }
      return resp;
    }

    return function cleanup() {
      source.cancel()
    }
  });

  useEffect(()=>{
    const range = mapRange ? mapRange : originalMapRangeRef.current;
    if (isBokehRendered){
      try{
        updateMap(plotRef.current, range);
      }
      catch{
        console.log(`Could not set range for ${targetId.current} at index ${graphIndex.current}`);
      }
    }
  },[mapRange, isBokehRendered]);

  useEffect(()=>{
    return function cleanup() {
      if (typeof getObjectProps(window, 'Bokeh', 'index',`${graphId}`,'model') === 'object'){
        window.Bokeh.index[graphId].model.document.clear();
        console.log(`Map index ${graphId} cleared!`);
      }
    }
  },[graphId]);

  console.log(`Graph ${targetId.current} component rendered!`);

  return (
    <div id={graphId}></div>
  );
}

export const updateMap = (plot, mapRange) => {
  // TODO: handle case where vars are undefined
  const bokehMapInfo = calculateMapInfo(
    plot.x_range.start,
    plot.x_range.end,
    plot.y_range.start,
    plot.y_range.end
  );

  const propMapInfo = calculateMapInfo(
    mapRange.xStart,
    mapRange.xEnd,
    mapRange.yStart,
    mapRange.yEnd
  );

  let xPadding = 0;
  let yPadding = 0;
  if (propMapInfo.aspectRatio < bokehMapInfo.aspectRatio){
    yPadding = propMapInfo.yRange * ((bokehMapInfo.aspectRatio/propMapInfo.aspectRatio)-1)/2;
  }
  else if (propMapInfo.aspectRatio > bokehMapInfo.aspectRatio){
    xPadding = propMapInfo.xRange * ((propMapInfo.aspectRatio/bokehMapInfo.aspectRatio)-1)/2;
  }
  plot.x_range.start = mapRange.xStart - xPadding;
  plot.x_range.end = mapRange.xEnd + xPadding;
  plot.y_range.start = mapRange.yStart - yPadding;
  plot.y_range.end = mapRange.yEnd + yPadding;
}

export const calculateMapInfo = (xStart, xEnd, yStart, yEnd) => {
  const info = {};
  info.yRange = yEnd - yStart;
  info.xRange = xEnd - xStart;
  info.aspectRatio = info.yRange/info.xRange;
  return info;
}

// TODO: docs
export const getObjectProps = (obj, level, ...rest) => {
  if (rest.length === 0 && obj !== undefined && obj[level] !== undefined) return obj[level];
  if (obj === undefined) return false;
  if (obj.hasOwnProperty(level)){
    return getObjectProps(obj[level], ...rest);
  } else {
    return false;
  }
}

const wait = (ms) => {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

export default BokehGraph;
