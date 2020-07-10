import React from 'react';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import '../style/style.css';

function TooltipOverlay({
  identifier, placement, tooltipText, component,
}) {
  return (
    <OverlayTrigger
      key={`${identifier}-overlay`}
      placement={placement}
      overlay={(
        <Tooltip id={`${identifier}-tooltip`}>{tooltipText}</Tooltip>
      )}
    >
      { component }
    </OverlayTrigger>
  );
}

TooltipOverlay.propTypes = forbidExtraProps({
  identifier: PropTypes.string.isRequired,
  placement: PropTypes.string.isRequired,
  tooltipText: PropTypes.string.isRequired,
  component: PropTypes.oneOfType([
    PropTypes.symbol, PropTypes.object,
  ]).isRequired,
});

export default TooltipOverlay;
