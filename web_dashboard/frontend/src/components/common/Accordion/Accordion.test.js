import React from 'react';
import { render, screen  } from '@testing-library/react';
import Accordion from './Accordion';
import userEvent from '@testing-library/user-event'

const TOGGLE = <div>big red button</div>;
const CHILD = <div>My baby is ugly!</div>;

describe(`<Accordion /> rendering`, () => {
  test(`renders without crashing`, () => {
    const { container } = render(<Accordion toggleEl={TOGGLE}>{CHILD}</Accordion>);
    expect(screen.getByText('big red button')).toBeInTheDocument();

    // NOTE: in general, we want to avoid testing classnames.
    // In this case, visiblility is set in the css, which RTL has no visibility into
    expect(container.getElementsByClassName('overflow-hidden').length).toBe(1);
    expect(container.getElementsByClassName('overflow-visible').length).toBe(0);
  });

  test(`renders as open when isOpenOverride is set`, () => {
    const { container } = render(<Accordion toggleEl={TOGGLE} isOpenOverride={true}>{CHILD}</Accordion>);
    expect(container.getElementsByClassName('overflow-visible').length).toBe(1);
  });
});

describe(`<Accordion /> interactions`, () => {
  test(`toggles child visibility when toggle is clicked`, () => {
    const { container } = render(<Accordion toggleEl={TOGGLE}>{CHILD}</Accordion>);
    expect(container.getElementsByClassName('overflow-visible').length).toBe(0);

    // show
    userEvent.click(screen.getByText('big red button'));
    expect(container.getElementsByClassName('overflow-visible').length).toBe(1);

    // hide again
    userEvent.click(screen.getByText('big red button'));
    expect(container.getElementsByClassName('overflow-visible').length).toBe(0);
  });

  test(`calls onToggle when toggle is clicked`, () => {
    const onToggle = jest.fn()
    render(<Accordion toggleEl={TOGGLE} onToggle={onToggle}>{CHILD}</Accordion>);

    userEvent.click(screen.getByText('big red button'));
    expect(onToggle).toHaveBeenCalled();
  });
});
