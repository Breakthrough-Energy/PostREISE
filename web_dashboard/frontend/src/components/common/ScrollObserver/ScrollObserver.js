import React from 'react';
import PropTypes from 'prop-types';

/*
  This component uses the browser's built-in Intersection Observer API to track
  when a page element has scrolled into view
  For reference see https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API

  IMPORTANT: THE ORDER AND NUMBER OF CHILDREN CANNOT CHANGE OR BE REARRANGED!
  This level of flexibility would require resetting the refs on every render.
  We would also need to disconnect the observer from the refs and then observe
  all of the new child refs. Each child would then report its status by calling
  this.props.handleIntersect(). Not only is that highly inefficient, if
  handleIntersect() happens to trigger a rerender, it may cause an infinite
  render cycle.

props (text taken from MDN)
  root: The element that is used as the viewport for checking visibility of
    the target. Must be the ancestor of the target. Defaults to the browser
    viewport if not specified or if null.

  rootMargin: Grow or shrink each side of the root element's bounding box
    before computing intersections

  threshold: Either a single number or an array of numbers which indicate at
    what percentage of the target's visibility the observer's callback should
    be executed. If you only want to detect when visibility passes the 50% mark,
    you can use a value of 0.5. If you want the callback to run every time
    visibility passes another 25%, you would specify the array [0, 0.25, 0.5,
    0.75, 1]. The default is 0 (meaning as soon as even one pixel is visible,
    the callback will be run). A value of 1.0 means that the threshold isn't
    considered passed until every pixel is visible.

  handleIntersect: Callback function, called when the element crosses the set
    threshold(s), BOTH entering and leaving. It is passed a list of entities
    and an Observer object.
*/
class ScrollObserver extends React.Component {
  constructor(props) {
    super(props);

    this.childRefs = React.Children.map(props.children, () =>
      React.createRef()
    );
  }

  componentDidMount() {
    const {
      handleIntersect,
      root=null,
      rootMargin="0px",
      threshold=0 } = this.props;

    this.observer = new IntersectionObserver(
      handleIntersect, { root, rootMargin, threshold });

    this.childRefs.forEach(ref => {
      this.observer.observe(ref.current);
    });
  }

  componentWillUnmount() {
    this.observer.disconnect();
  }

  renderChild = (child, i) => {
    return React.cloneElement(child, { ref: this.childRefs[i] });
  }

  render() {
    const {
      handleIntersect,
      root,
      rootMargin,
      threshold,
      children,
      ...otherProps } = this.props;

    return (
      <div {...otherProps}>
        {React.Children.map(children, this.renderChild)}
      </div>
    );
  }
}

ScrollObserver.propTypes = {
  root: PropTypes.element,
  rootMargin: PropTypes.string,
  threshold: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.arrayOf(PropTypes.number)]),
  handleIntersect: PropTypes.func
}

export default ScrollObserver;
