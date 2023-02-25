import React, { useEffect, useRef, useState } from 'react';
import { COLORS_RGB } from '../../../data/colors';
import { connect } from 'react-redux';
import DeckGL from '@deck.gl/react';
import { FlyToInterpolator, WebMercatorViewport } from 'react-map-gl';
import { GeoJsonLayer } from '@deck.gl/layers';
import PropTypes from 'prop-types';
import { STATES } from '../../../data/states_lat_lon';

import './DeckGLMap.css';


// These come from the store and get inserted into our props
const mapStateToProps = state => ({ stateShapefiles: state.dashboardSlice.stateShapefiles });

const DeckGLMap = ({ layers, getTooltip = null, location = 'Show All', onLocationClick, highlightStateOnHover = true, canPanZoom = true, children, stateShapefiles }) => {
  const deckRef = useRef(null);
  const [ dataLoaded, setDataLoaded ] = useState(false);
  const [ hoveredLocation, setHoveredLocation ] = useState(null);

  // Size of map is passed to the viewport to get correct zoom level
  const sizeElRef = useRef(null);
  const sizeRef = useRef(null);

  // passing a function to useState() means lazy initialization
  // i.e. getViewportByLocation is not run on each render
  const [ viewport, setViewport ] = useState(() => getViewportByLocation({ location }));

  useEffect(() => {
    if (sizeElRef.current) {
      sizeRef.current = {
        width: sizeElRef.current.clientWidth,
        height: sizeElRef.current.clientHeight
      }
    }
  }, []);

  // Add listener to update viewport if the map changes location or is resized
  useEffect(() => {
    setViewport(getViewportByLocation({ location, size: sizeRef.current }));

    const resizeObserver = new ResizeObserver(entries => {
      // TODO; test firefox. entry.contentBoxSize?
      const { width, height } = entries[0].contentRect;
      sizeRef.current = { width, height };
      setViewport(getViewportByLocation({ location, size: sizeRef.current }));
    });

    resizeObserver.observe(sizeElRef.current);

    // Used for return function
    const sizeElRefCopy = sizeElRef.current;
    return () => {
      resizeObserver.unobserve(sizeElRefCopy);
    }
  }, [ location ]);

  const onClick = info => {
    const clickedLocation = deckRef.current.pickObject({
      x: info.x,
      y: info.y,
      layerIds: [ 'states-layer' ]
    });

    let locationName = clickedLocation ? clickedLocation.object.properties.NAME : 'Show All';
    if (locationName === 'Texas') {
      locationName = 'Texas Interconnect';
    }
    onLocationClick(locationName);
  };

  const onHover = info => {
    const hoverData = deckRef.current.pickObject({
      x: info.x,
      y: info.y,
      radius: 5,
      layerIds: [ 'states-layer' ]
    });
    const newHoveredLocation = hoverData && hoverData.object.properties.NAME;

    if (hoveredLocation !== newHoveredLocation) {
      setHoveredLocation(newHoveredLocation);
    }
  };

  const pickTooltip = data => {
    if (data.layer !== null) {
      const pickedObjects = deckRef.current.pickMultipleObjects({
        x: data.x,
        y: data.y,
        radius: 3,
        depth: 10 // Limit to 10 items in tooltip. Max is 99
      });

      const tooltip = getTooltip(pickedObjects);
      let tooltipContent;
      if (tooltip && tooltip.html) {
        tooltipContent = tooltip.html;
      } else if (typeof tooltip === 'string' && tooltip !== '') {
        tooltipContent = tooltip;
      } else {
        return null;
      }
      return {
        html: tooltipContent,
        style: { // styles the div controlled by deckgl
          zIndex: 9000,
          padding: '10px',
          whiteSpace: "pre-wrap",
        }
      }
    }
  }

  const getStateColors = d => {
    if (d && d.properties.NAME === hoveredLocation) {
      return COLORS_RGB.blueHighlight;
    } else {
      return COLORS_RGB.clear;
    }
  }

  const baseMap = new GeoJsonLayer({
    id: 'states-layer',
    data: stateShapefiles,
    onDataLoad: () => {
      requestAnimationFrame(() => setDataLoaded(true))
    },
    pickable: true,
    filled: true,
    getFillColor: highlightStateOnHover ? getStateColors : COLORS_RGB.clear,
    wireframe: true,
    lineWidthMinPixels: 1,
    getLineColor: dataLoaded ? COLORS_RGB.black : COLORS_RGB.clear,
    updateTriggers: {
      getLineColor: dataLoaded,
      getFillColor: hoveredLocation
    },
    transitions: {
      getLineColor: 375
    },
  });

  return (
    <div className="deck-gl-map" ref={sizeElRef}>
      <DeckGL
        ref={deckRef}
        initialViewState={viewport}
        controller={canPanZoom}
        layers={[ baseMap, ...layers ]}
        onClick={onClick}
        onHover={onHover}
        getTooltip={getTooltip ? pickTooltip : null}>
          {children}
      </DeckGL>
    </div>
  );
};

const getViewportByLocation = ({ location, size }) => {
  if (location === 'Texas') {
    location = 'Texas Interconnect';
  }

  const { xmin, ymin, xmax, ymax } = STATES[location];
  const viewportWebMercator = new WebMercatorViewport(size || { width: window.innerWidth, height: window.innerHeight });

  const {longitude, latitude, zoom} = viewportWebMercator.fitBounds(
    [[ xmin, ymin ], [ xmax, ymax ]],
    { padding: 20 }
  );

  return {
    longitude,
    latitude,
    zoom,
    transitionInterpolator: new FlyToInterpolator(),
    transitionDuration: 'auto'
  };
};

DeckGLMap.propTypes = {
  layers: PropTypes.array,
  getTooltip: PropTypes.func,
  location: PropTypes.string,
  onLocationClick: PropTypes.func,
  highlightStateOnHover: PropTypes.bool,
  canPanZoom: PropTypes.bool,
  children: PropTypes.node
}

DeckGLMap.defaultProps = {
  getTooltip: null,
  location: 'Show All',
  highlightStateOnHover: true,
  canPanZoom: true,
}

export default connect(mapStateToProps)(DeckGLMap);
