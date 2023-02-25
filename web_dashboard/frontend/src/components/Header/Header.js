import React from 'react';
import { A } from 'hookrouter';
import classNames from 'classnames';
import useOpenClose from '../../hooks/useOpenClose/useOpenClose';

import '../common/css/Helpers.css';
import '../common/css/Variables.css';
import './Header.css';

export const HEADER_THEME = {
  CLEAR: 'clear',
  WHITE: 'white',
  BLUE_BG: 'blue_bg'
};

const Header = ({ className, theme = HEADER_THEME.CLEAR }) => {
  const { isOpen } = useOpenClose();
  const headerTheme = isOpen ? HEADER_THEME.WHITE : theme;
  const headerClass = classNames('header', `header__${headerTheme}`, className, { header__nav__open: isOpen });

  return (
    <header className={headerClass}>
      <div className="header__top">
        <A className="header__logo reset-link-styles" href="/">
          <div className="header__title">REISE Dashboard</div>
        </A>
      </div>
    </header>
  );
}

export default Header;
