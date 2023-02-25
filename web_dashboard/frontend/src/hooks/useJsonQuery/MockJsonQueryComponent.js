import React from 'react';
import useJsonQuery from './useJsonQuery';

const isPromise = obj => Boolean(obj && typeof obj.then === 'function')

const MockJsonQueryComponent = ({ url, options }) => {
  const { loading, error, data  } = useJsonQuery(url, options);

  return (
    <div className="mock-json-query-component">
      {loading && <p>loading</p>}
      {error && <p>error</p>}
      {data &&
        <>
          <p>data</p>
          <p>{isPromise(data) ? 'promise' : JSON.stringify(data)}</p>
        </>
      }
    </div>
  );
}

export default MockJsonQueryComponent;
