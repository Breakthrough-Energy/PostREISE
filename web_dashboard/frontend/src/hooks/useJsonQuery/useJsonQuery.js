import { useEffect, useReducer } from "react";
import { JSONLoader } from '@loaders.gl/json';
import { load } from '@loaders.gl/core';

const initialState = { loading: true, error: false, data: null };

const reducer = (state, { type, payload }) => {
  switch (type) {
    case 'load':
      return { loading: true, error: false, data: payload.dataPromise };
    case 'error':
      return { loading: false, error: payload.error, data: null };
    case 'success':
      return { loading: false, error: false, data: payload.data };
    default:
      return state;
  }
}

/**
 * Handles logic for loading json data from a URL
 * Returns values for loading, error, and data
 * Data is a promise while loading
 */
const useJsonQuery = (url, options = { skip: false }) => {
  const [{ loading, error, data }, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    const loadData = async () => {
      const dataPromise = load(url, JSONLoader);
      dispatch({ type: 'load', payload: { dataPromise } });

      try {
        const data = await dataPromise;
        dispatch({ type: 'success', payload: { data } });
      } catch(error) {
        console.log(error);
        dispatch({ type: 'error', payload: { error } });
      }
    }

    if (!options.skip) {
      loadData();
    }
  }, [ url, options.skip ]);

  return { loading, error, data };
};

export default useJsonQuery;
