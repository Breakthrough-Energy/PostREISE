import React from 'react';
import {render, screen} from '@testing-library/react';
import Link from './Link';

test(`can display link contents`, () => {
    const linkText = `Still I Rise`;
    render(<Link>{linkText}</Link>)

    expect(screen.getByText(linkText)).toBeInTheDocument()
})