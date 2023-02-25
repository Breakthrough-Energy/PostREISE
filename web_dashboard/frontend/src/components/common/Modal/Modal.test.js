import React from 'react';
import { mount } from 'enzyme';
import Modal from './Modal';

afterEach(() => {
  const modalRoot = global.document.querySelector('#modal-root');
  modalRoot.remove();
});

describe('<Modal /> rendering', () => {
  test('renders without crashing', () => {
    // Start with no modal root
    let modalRoot = global.document.querySelector('#modal-root');
    expect(modalRoot).toBeNull();

    const wrapper = mount(<Modal className="foo">Hello!</Modal>);
    expect(wrapper.find('.modal.foo')).toHaveLength(1);
    expect(wrapper.contains('Hello!')).toBe(true);

    // Modal creates #modal-root div if none exists
    modalRoot = global.document.querySelector('#modal-root');
    expect(modalRoot).toBeTruthy();
    expect(modalRoot.childNodes.length).toBe(1);
    expect(global.document.querySelector('.modal__fullscreen')).toBeNull();

    wrapper.unmount();

    // Modal cleans up child after unmount, but not #modal-root
    expect(global.document.querySelector('.foo')).toBeNull();
    expect(modalRoot).toBeTruthy();
  });

  test('uses existing #modal-root if available', () => {
    const modalRoot = global.document.createElement("div");
    modalRoot.setAttribute("id", "modal-root");
    const body = global.document.querySelector('body');
    body.appendChild(modalRoot);

    const wrapper = mount(<Modal className="foo">Hello!</Modal>);
    expect(wrapper.find('.modal.foo')).toHaveLength(1);
    expect(wrapper.contains('Hello!')).toBe(true);

    // Make sure a second #modal-root has not been added
    expect(body.childNodes.length).toBe(1);

    wrapper.unmount();

    expect(modalRoot).toBeTruthy();
  });

  test('renders a full screen element if fullscreen prop is True', () => {

    const wrapper = mount(<Modal className="foo" fullscreen>Hello!</Modal>);
    expect(global.document.querySelector('.modal__fullscreen')).toBeTruthy();
    expect(wrapper.find('.modal.foo')).toHaveLength(1);
    expect(wrapper.contains('Hello!')).toBe(true);

    wrapper.unmount();

    expect(global.document.querySelector('.modal__fullscreen')).toBeNull();
    expect(global.document.querySelector('.foo')).toBeNull();
  });
});
