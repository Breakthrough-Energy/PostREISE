import React from 'react';
import {render, screen} from '@testing-library/react';
import H2Korolev from './H2Korolev';

test(`can display headers`, () => {
    const header = 'On the Pulse of Morning';
    render(<H2Korolev>{header}</H2Korolev>)

    expect(screen.getByText(header)).toBeInTheDocument()
})