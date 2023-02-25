import React from 'react';
import { shallow } from 'enzyme';
import Select from './Select';

const OPTIONS = {
  chicken: {
    text: 'Chicken',
    infoBox: (<div><p>noun</p><p>a domestic fowl kept for its eggs or meat, especially a young one</p></div>)
  },
  with: {
    text: 'With',
    infoBox: (<div><p>preposition</p><p>accompanied by (another person or thing)</p></div>)
  },
  rice: {
    text: 'Rice',
    infoBox: (<div><p>noun</p><p>a swamp grass which is widely cultivated as a source of food, especially in Asia</p></div>)
  }
};

describe('<Select /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    expect(wrapper.state('isOpen')).toBe(false);
  });

  test('renders options when open', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    wrapper.setState({isOpen: true});
    expect(wrapper.find('.select__option')).toHaveLength(3);
  });

  test('does not render options when closed', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    expect(wrapper.find('.select__option')).toHaveLength(0);
  });
});

describe('<Select /> lifecycle methods', () => {
  // Learn more about this testing event listeners: https://medium.com/@DavideRama/testing-global-event-listener-within-a-react-component-b9d661e59953
  // Learn more about spying on class property functions: https://remarkablemark.org/blog/2018/06/13/spyon-react-class-method/
  test('componentDidMount adds an event listener that calls checkForBlur on click', () => {
    // Fake addEventListener func
    const map = {};
    document.addEventListener = jest.fn((event, callbackFn) => {
      map[event] = callbackFn;
    });

    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    expect(document.addEventListener).toHaveBeenCalledTimes(1);

    // Spy on checkForBlur func
    const checkForBlurSpy = jest.spyOn(wrapper.instance(), 'checkForBlur');

    // Rerun componentDidMount so addEventListener uses the spied function as its callback
    wrapper.instance().componentDidMount();

    // Simulate click event
    map.mousedown({ target: 'foo' });

    expect(checkForBlurSpy).toHaveBeenCalledTimes(1);
  });

  test('componentWillUnmount removes the event listener', () => {
    const map = {};
    document.removeEventListener = jest.fn((event, callbackFn) => {
      map[event] = callbackFn;
    });

    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    wrapper.instance().componentWillUnmount();

    expect(document.removeEventListener).toHaveBeenCalledTimes(1);
  });
});

describe('<Select /> interactions', () => {
  test('opens and closes when select button is clicked', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);

    // click once to open
    wrapper.simulate('click');
    expect(wrapper.instance().state['isOpen']).toBe(true);

    // click again to close
    wrapper.simulate('click');
    expect(wrapper.instance().state['isOpen']).toBe(false);
  });

  test('on option clicked calls parent func onOptionClicked and closes', () => {
    const onOptionClicked = jest.fn();
    const wrapper = shallow(<Select value="chicken" options={OPTIONS} onOptionClicked={onOptionClicked}/>);
    wrapper.setState({isOpen: true});

    const riceOption = wrapper.find('.select__option').at(2);
    riceOption.simulate('click');

    expect(onOptionClicked).toHaveBeenCalledTimes(1);
    expect(onOptionClicked).toHaveBeenCalledWith('rice');
    expect(wrapper.instance().state['isOpen']).toBe(false);
    expect(wrapper.instance().state['optionHovering']).toEqual(null)
  });

  test('closes on blur', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS}/>);
    wrapper.setState({isOpen: true});

    wrapper.simulate('blur');
    expect(wrapper.instance().state['isOpen']).toBe(false);
    expect(wrapper.instance().state['optionHovering']).toEqual(null)
  });
});

describe('<Select /> infobox', () => {
  test('renders when select is open and info is set to true', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS} showInfoBox={true} />);

    wrapper.setState({isOpen: true});
    expect(wrapper.find('.select__infobox')).toHaveLength(1);
  });

  test('does not render when select is open and info is not set to true', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS} />);

    wrapper.setState({isOpen: true});
    expect(wrapper.find('.select__infobox')).toHaveLength(0);
  });

  test('renders correct option info on hover and defaults to selected value', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS} showInfoBox={true} />);

    wrapper.setState({isOpen: true});

    const chickenText = 'a domestic fowl kept for its eggs or meat, especially a young one';
    expect(wrapper.contains(chickenText)).toBe(true);

    const riceOption = wrapper.find('.select__option').at(2);
    riceOption.simulate('mouseEnter');

    const riceText = 'a swamp grass which is widely cultivated as a source of food, especially in Asia';
    expect(wrapper.contains(riceText)).toBe(true);
  });

  test('resets hover option on close', () => {
    const wrapper = shallow(<Select value="chicken" options={OPTIONS} showInfoBox={true} />);

    wrapper.setState({isOpen: true});
    const withOption = wrapper.find('.select__option').at(1);
    withOption.simulate('mouseEnter');

    expect(wrapper.instance().state['optionHovering']).toEqual('with')

    wrapper.instance().close();
    expect(wrapper.instance().state['optionHovering']).toEqual(null)

    wrapper.instance().toggleOpen();
    expect(wrapper.instance().state['optionHovering']).toEqual(null)
  });
});
