import React from 'react';
import {render, screen} from '@testing-library/react';
import MaxWidthContent from './MaxWidthContent';

test(`can display it's content at full width`, () => {
    const poemTitle = 'California Prodigal';
    render(<MaxWidthContent>{poemTitle}</MaxWidthContent>)

    expect(screen.getByText(poemTitle)).toBeInTheDocument()
})