import React from 'react';
import PropTypes from 'prop-types';

import './H2Korolev.css';

const H2Korolev = ({className, children}) => <h2 className={'h2-korolev ' + className}>{children}</h2>;

H2Korolev.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node
}

H2Korolev.defaultProps = {
    className: ''
}
export default H2Korolev;