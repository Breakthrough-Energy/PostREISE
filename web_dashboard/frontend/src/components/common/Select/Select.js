import React from 'react';
import classNames from 'classnames';
import { IoIosArrowDown } from 'react-icons/io';
import PropTypes from 'prop-types';

import EllipsisText from '../EllipsisText/EllipsisText.js';

import '../css/Variables.css';
import './Select.css';

// We create our own select component beccause the built-in
// select element is not possible to style
class Select extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isOpen: false,
      optionHovering: null
    };
  }

  componentDidMount() {
    document.addEventListener('mousedown', this.checkForBlur, false)
  }

  componentWillUnmount() {
    document.removeEventListener('mousedown', this.checkForBlur, false)
  }

  // This handles a bug in firefox on mac where blur events are not handled correctly
  // See https://github.com/facebook/react/issues/12993#issuecomment-413949427
  checkForBlur = (e) => {
    if (this.state.isOpen
      && e
      && e.target
      && !this.selectRef.contains(e.target)) {
      this.onBlur()
    }
  }

  close = () => {
    this.setState({isOpen: false, optionHovering: null});
  }

  toggleOpen = () => {
    this.setState({isOpen: !this.state.isOpen, optionHovering: null});
  }

  onBlur = () => {
    this.close();
  }

  onOptionClicked = (key) => {
    this.props.onOptionClicked(key);
    this.close();
  }

  onOptionHover = (key) => {
    this.setState({optionHovering: key})
  }

  renderInfoBox = () => {
    const {options, value} = this.props;

    // if the mouse is hovering over an option, show it. Else show selected val
    const scenarioId = this.state.optionHovering || value;
    const {text, infoBox} = options[scenarioId];

    return (
      <div className="select__infobox">
        <h3 className="select__infobox__title">{text}</h3>
        {infoBox}
      </div>
    );
  }

  renderOptions = () => {
    return(
      <div className="select__options">
        {Object.entries(this.props.options).map(([key, {text}]) =>
          <EllipsisText
            className="select__option"
            key={key}
            onMouseEnter={this.onOptionHover.bind(this, key)}
            onClick={this.onOptionClicked.bind(this, key)}>
            {text}
          </EllipsisText>
        )}
      </div>
    );
  }

  render() {
    const {className, options, showInfoBox, value} = this.props;
    const {isOpen} = this.state;

    return(
      <button
        className={classNames(className, 'select', {'select__open': isOpen})}
        ref={selectRef => this.selectRef = selectRef}
        onClick={this.toggleOpen}
        onBlur={this.onBlur} >
        <EllipsisText className="select__buttonText">
          {options[value]['text']}
        </EllipsisText>
        <IoIosArrowDown className="select__arrow"/>
        {isOpen &&
          <div className="select__dropdown" >
            {this.renderOptions()}
            {showInfoBox && this.renderInfoBox()}
          </div>
        }
      </button>
    );
  }
}

Select.propTypes = {
  className: PropTypes.string,
  options: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.object,
      PropTypes.string
    ])
  ),
  onOptionClicked: PropTypes.func,
  showInfoBox: PropTypes.bool,
  value: PropTypes.string
}
export default Select;
