import React from 'react';
import { render, screen } from '@testing-library/react';
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import MockJsonQueryComponent from './MockJsonQueryComponent';

// Tests based on https://redux.js.org/usage/writing-tests#example-1

// We use msw to intercept the network request during the test
export const handlers = [
  rest.get('/1270/pg', (req, res, ctx) => {
    return res(ctx.json('very important data'));
  }),
  rest.get('/fake-error', (req, res, ctx) => {
    return res(ctx.status(404));
  }),
];

const server = setupServer(...handlers)
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('useJsonQuery', () => {
  test('useJsonQuery fetches and receives data', async () => {
    render(<MockJsonQueryComponent url="/1270/pg" />);

    expect(screen.getByText('loading')).toBeInTheDocument();
    expect(screen.getByText('promise')).toBeInTheDocument();
    expect(screen.queryByText('error')).not.toBeInTheDocument();

    // wait for request to return
    expect(await screen.findByText('"very important data"')).toBeInTheDocument();
    expect(screen.queryByText('loading')).not.toBeInTheDocument();
    expect(screen.queryByText('error')).not.toBeInTheDocument();
  });

  test('useJsonQuery catches errors', async () => {
    render(<MockJsonQueryComponent url="/fake-error" />);

    // wait for request to return
    expect(await screen.findByText('error')).toBeInTheDocument();
    expect(screen.queryByText('loading')).not.toBeInTheDocument();
    expect(screen.queryByText('data')).not.toBeInTheDocument()
  });
});
