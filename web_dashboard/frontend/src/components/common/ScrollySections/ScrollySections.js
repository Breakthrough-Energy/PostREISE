import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';
import ScrollObserver from '../ScrollObserver/ScrollObserver';

/* Until we add more complex props, this component expects each child to be
 * at least 480px high.
 */

class ScrollySections extends React.Component {
  // These variables are not in the state because they do not trigger rerender

  // Sections that are partly or entirely within the intersection window
  // Should be in the same order as the sections on the page
  visibleSections = [];
  // We have special behavior when the page has just loaded, but after the
  // component has mounted
  isFirstLoad = true;

  addSection = (section) => {
    if (this.visibleSections.includes(section)) {
      console.log("ERROR: trying to add section twice", section);
    } else {
      this.visibleSections.push(section);

      // Make sure sections are in the same order as sections on the page
      this.visibleSections.sort((a, b) =>
        this.props.keys.indexOf(a) - this.props.keys.indexOf(b)
      );
    }
  }

  removeSection = (section) => {
    if (!this.visibleSections.includes(section)) {
      // On first load every section reports its status
      if (!this.isFirstLoad) {
        console.log("ERROR: trying to remove a section not in list", section);
      }
    } else {
      this.visibleSections.splice(this.visibleSections.indexOf(section), 1);
    }
  }

  // If we have two visible sections we must choose one to show
  // entries: list of objects passed back from IntersectionObserver,
  // one entry for each section that entered or left the intersection window
  // As per the w3C spec, entries will always be ordered in same order as
  // observe() was called. Thus we can trust the entry order to match the
  // order of elements on the page.
  // See: https://w3c.github.io/IntersectionObserver/#update-intersection-observations-algo
  // under section 2.2
  chooseNewSection = (entries) => {
    const { handleSectionChange } = this.props;

    if (this.isFirstLoad) {
      handleSectionChange(this.visibleSections[1]);
    } else {
      // If we are scrolling downwards, the top section is disappearing and the
      // active section should be the highest visible section on the page
      // If we are scrolling upwards, the top section is coming into view and
      // the active section should be the lowest visible section on the page
      const scrollingDownwards = !entries[0].isIntersecting;
      if (scrollingDownwards) {
        handleSectionChange(this.visibleSections[0]);
      } else {
        handleSectionChange(this.visibleSections[1]);
      }
    }
  }

  // We change the active section when it LEAVES the intersection window
  // entries: list of objects passed back from IntersectionObserver,
  // one entry for each section that entered or left the intersection window
  // NOTE: There is an unused argument available --
  // IntersectionObserver also passes back its Observer but we don't need it
  handleIntersectionEvent = (entries) => {
    const { activeSection, handleSectionChange } = this.props;

    // Update list of visible sections
    entries.forEach(entry => {
      const key = entry.target.id;
      entry.isIntersecting ? this.addSection(key) : this.removeSection(key);
    });

    const visLength = this.visibleSections.length;
    if (visLength > 2) {
      console.log("ERROR: Too many visible sections",
        this.visibleSections, activeSection);
    }

    // Change active section if necessary
    const activeSectionHasLeft = !this.visibleSections.includes(activeSection);
    if (activeSectionHasLeft) {
      // Skip visLength === 0. If no sections are visible, we're on a different
      // part of the page and don't need to do anything

      if (visLength === 1) {
        handleSectionChange(this.visibleSections[0]);

      } else if (visLength === 2) {
        this.chooseNewSection(entries);
      }
    }

    this.isFirstLoad = false;
  }

  // Calculate the breakpoint for switching over to the next section
  getMargin = () => {
    const height = document.documentElement.clientHeight;
    const intersectionWindow = this.props.intersectionWindowHeight || .2 * height; // used to be 220, which worked well
    return -0.5 * (height - intersectionWindow);
  }

  // Wrap all children in a div with an id set
  renderChild = (child, i) => {
    return <div id={this.props.keys[i]}>{child}</div>
  }

  render() {
    const { className, children } = this.props;
    const scrollyClass = classNames('scrollysections', className);

    return (
      <ScrollObserver
        className={scrollyClass}
        rootMargin={`${this.getMargin()}px 0px`}
        handleIntersect={this.handleIntersectionEvent} >
        {React.Children.map(children, this.renderChild)}
      </ScrollObserver>
    );
  }
}

ScrollySections.propTypes = {
  activeSection: PropTypes.string,
  className: PropTypes.string,
  children: PropTypes.node,
  handleSectionChange: PropTypes.func,
  intersectionWindowHeight: PropTypes.number,
  keys: PropTypes.string
}
export default ScrollySections;
