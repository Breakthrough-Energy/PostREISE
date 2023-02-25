import React from 'react';
import { A } from 'hookrouter';
import classNames from 'classnames';
import { FaArrowRight } from 'react-icons/fa';
import Link from '../Link/Link';
import PropTypes from 'prop-types';
import { routes } from '../../App/App';

import '../css/Variables.css';
import './IconButtonLink.css';

export const BUTTON_THEME = {
  WHITE: 'white',
  BLUE: 'blue'
};

const IconButtonLink = ({ className, href, Icon, theme, children }) => {
  const iconButtonLinkClass = classNames(
    className,
    'icon-button-link',
    `icon-button-link__${theme}`,
    'flex-center',
    'reset-link-styles');

  // We use hookRouter (A) for internal routing and Link for external urls.
  // TODO: we will need to update this once we have more complex routes
  // For now, simple matching is good enough.
  const isInternalLink = routes[href] !== undefined;
  const LinkComponent = isInternalLink ? A : Link;

  return (
    <div className="gradient-button__wrapper">
      <div className="gradient-button__shadow"></div>
      <LinkComponent className={iconButtonLinkClass} href={href} >
        {children}
        <div className="icon-button-link__icon flex-center">
          <Icon />
        </div>
      </LinkComponent>
    </div>
  )
};

IconButtonLink.propTypes = {
  className: PropTypes.string,
  href: PropTypes.string,
  Icon: PropTypes.elementType,
  theme: PropTypes.oneOf([ BUTTON_THEME.WHITE, BUTTON_THEME.BLUE ]),
  children: PropTypes.node
}

IconButtonLink.defaultProps = {
  Icon: FaArrowRight,
  theme: BUTTON_THEME.WHITE
}

export default IconButtonLink;
