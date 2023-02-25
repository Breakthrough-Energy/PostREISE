import React from 'react';
import PropTypes from 'prop-types';

const Link = ({ className, href, children }) => {
  return (
    <a
      className={'link ' + className}
      href={href}
      target="_blank"
      rel="noopener noreferrer">
      {children}
    </a>
  );
};

Link.propTypes = {
  className: PropTypes.string,
  href: PropTypes.string,
  children: PropTypes.node
}

Link.defaultProps = {
  className: "",
}

export default Link;
