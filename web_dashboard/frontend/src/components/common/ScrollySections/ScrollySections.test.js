import React from 'react';
import { shallow } from 'enzyme';
import ScrollySections from './ScrollySections';
import ScrollObserver from '../ScrollObserver/ScrollObserver';

const PROPS = {
  keys: ['bulbasaur', 'charmander', 'squirtle'],
  children: [
    <p>bulbasaur</p>,
    <p>charmander</p>,
    <p>squirtle</p>
  ],
  activeSection: 'charmander',
  handleSectionChange: () => {}
}

describe('<ScrollySections /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<ScrollySections {...PROPS} />);
    expect(wrapper.find(ScrollObserver)).toHaveLength(1);
    expect(wrapper.instance().isFirstLoad).toBe(true);
    expect(wrapper.instance().visibleSections).toEqual([]);
  });
});

describe('<ScrollySections /> business logic', () => {
  test('getMargin returns correct result', () => {
    jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementation(() => 1000);

    const wrapper = shallow(<ScrollySections {...PROPS} />);
    expect(wrapper.instance().getMargin()).toBe(-400);
  });

  test('getMargin returns correct result when the intersectionWindowHeight is set', () => {
    jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementation(() => 1000);

    const wrapper = shallow(<ScrollySections {...PROPS} intersectionWindowHeight={300}/>);
    expect(wrapper.instance().getMargin()).toBe(-350);
  });

  describe('add and remove sections', () => {
    test('addSection adds a section to visibleSections', () => {
      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().addSection('bulbasaur');
      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur']);
    });

    test('addSection does not add a section twice and logs an error to console', () => {
      console.log = jest.fn();

      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().visibleSections = ['bulbasaur', 'charmander'];

      wrapper.instance().addSection('bulbasaur');
      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur', 'charmander']);
      expect(console.log).toHaveBeenCalledTimes(1);
    });

    test('addSection maintains the original order of the sections', () => {
      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().visibleSections = ['charmander'];
      wrapper.instance().addSection('bulbasaur');
      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur', 'charmander']);
    });

    test('removeSection removes a section to visibleSections', () => {
      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().visibleSections = ['bulbasaur', 'charmander'];
      wrapper.instance().isFirstLoad = false;

      wrapper.instance().removeSection('bulbasaur');
      expect(wrapper.instance().visibleSections).toEqual(['charmander']);
    });

    test('removeSection does not try to remove a section if it is not visible and logs an error to console', () => {
      console.log = jest.fn();

      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().visibleSections = ['bulbasaur', 'charmander'];
      wrapper.instance().isFirstLoad = false;

      wrapper.instance().removeSection('squirtle');
      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur', 'charmander']);
      expect(console.log).toHaveBeenCalledTimes(1);
    });

    test('removeSection does not log to the console if it is first load and we try to remove a section when it is not visible', () => {
      console.log = jest.fn();

      const wrapper = shallow(<ScrollySections {...PROPS} />);
      wrapper.instance().visibleSections = ['bulbasaur', 'charmander'];
      wrapper.instance().isFirstLoad = true;

      wrapper.instance().removeSection('squirtle');
      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur', 'charmander']);
      expect(console.log).toHaveBeenCalledTimes(0);
    });
  });

  describe('chooseNewSection', () => {
    test('chooseNewSection chooses bottom section on first page load', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'bulbasaur' }, isIntersecting: false },
        { target: { id: 'charmander' }, isIntersecting: true },
        { target: { id: 'squirtle' }, isIntersecting: true }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'bulbasaur'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().isFirstLoad = true;
      wrapper.instance().visibleSections = ['charmander', 'squirtle'];

      wrapper.instance().chooseNewSection(entries);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(1);
      expect(mockHandleSectionChange).toHaveBeenCalledWith('squirtle');
    });

    test('chooseNewSection chooses top section when scrolling down', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [ { target: { id: 'bulbasaur' }, isIntersecting: false } ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'bulbasaur'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().isFirstLoad = false;
      wrapper.instance().visibleSections = ['charmander', 'squirtle'];

      wrapper.instance().chooseNewSection(entries);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(1);
      expect(mockHandleSectionChange).toHaveBeenCalledWith('charmander');
    });

    test('chooseNewSection chooses bottom section when scrolling up', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [ { target: { id: 'bulbasaur' }, isIntersecting: true } ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'squirtle'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().isFirstLoad = false;
      wrapper.instance().visibleSections = ['bulbasaur', 'charmander'];

      wrapper.instance().chooseNewSection(entries);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(1);
      expect(mockHandleSectionChange).toHaveBeenCalledWith('charmander');
    });
  });

  describe('handleIntersectionEvent', () => {
    test('handleIntersectionEvent calls addSection and removeSection and sets isFirstLoad to false', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'bulbasaur' }, isIntersecting: true },
        { target: { id: 'charmander' }, isIntersecting: true },
        { target: { id: 'squirtle' }, isIntersecting: false }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'squirtle'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['squirtle'];
      wrapper.instance().isFirstLoad = true;
      wrapper.instance().addSection = jest.fn();
      wrapper.instance().removeSection = jest.fn();

      wrapper.instance().handleIntersectionEvent(entries);

      expect(wrapper.instance().addSection).toHaveBeenCalledTimes(2);
      expect(wrapper.instance().addSection).toHaveBeenCalledWith('bulbasaur');
      expect(wrapper.instance().addSection).toHaveBeenCalledWith('charmander');
      expect(wrapper.instance().removeSection).toHaveBeenCalledTimes(1);
      expect(wrapper.instance().removeSection).toHaveBeenCalledWith('squirtle');
      expect(wrapper.instance().isFirstLoad).toBe(false);
    });

    test('handleIntersectionEvent logs an error if there are more than two visible sections', () => {
      console.log = jest.fn();
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'charmander' }, isIntersecting: true },
        { target: { id: 'squirtle' }, isIntersecting: true }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'bulbasaur'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['bulbasaur'];

      wrapper.instance().handleIntersectionEvent(entries);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(0);
      expect(console.log).toHaveBeenCalledTimes(1);
    });

    test('handleIntersectionEvent does not call this.props.handleSectionChange if the active section is still visible', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'bulbasaur' }, isIntersecting: true }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'charmander'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['charmander'];

      wrapper.instance().handleIntersectionEvent(entries);

      expect(wrapper.instance().visibleSections).toEqual(['bulbasaur', 'charmander']);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(0);
    });

    test('handleIntersectionEvent does not call this.props.handleSectionChange if the entire scrollysections is no longer in view', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'charmander' }, isIntersecting: false },
        { target: { id: 'squirtle' }, isIntersecting: false }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'charmander'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['charmander', 'squirtle'];

      wrapper.instance().handleIntersectionEvent(entries);

      expect(wrapper.instance().visibleSections).toEqual([]);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(0);
    });

    test('handleIntersectionEvent calls this.props.handleSectionChange if the active section has left and there is only one visible section', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'charmander' }, isIntersecting: false }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'charmander'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['charmander', 'squirtle'];

      wrapper.instance().handleIntersectionEvent(entries);

      expect(wrapper.instance().visibleSections).toEqual(['squirtle']);
      expect(mockHandleSectionChange).toHaveBeenCalledTimes(1);
      expect(mockHandleSectionChange).toHaveBeenCalledWith('squirtle');
    });

    test('handleIntersectionEvent calls chooseNewSection if the active section has left and there are two visible sections', () => {
      const mockHandleSectionChange = jest.fn();
      const entries = [
        { target: { id: 'bulbasaur' }, isIntersecting: false },
        { target: { id: 'charmander' }, isIntersecting: true },
        { target: { id: 'squirtle' }, isIntersecting: true }
      ];

      const wrapper = shallow(<ScrollySections {...PROPS} activeSection={'bulbasaur'} handleSectionChange={mockHandleSectionChange} />);
      wrapper.instance().visibleSections = ['bulbasaur'];
      wrapper.instance().chooseNewSection = jest.fn();

      wrapper.instance().handleIntersectionEvent(entries);

      expect(wrapper.instance().visibleSections).toEqual(['charmander', 'squirtle']);
      expect(wrapper.instance().chooseNewSection).toHaveBeenCalledTimes(1);
      expect(wrapper.instance().chooseNewSection).toHaveBeenCalledWith(entries);
    });
  });
});
