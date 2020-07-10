import React from 'react';
import Collapsible from 'react-collapsible';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import '../../style/style.css';

function CollapsibleForm({
  trigger, triggerClassName, triggerOpenedClassName, triggerDisabled, open,
  content,
}) {
  return (
    <Collapsible
      trigger={trigger}
      triggerClassName={triggerClassName}
      triggerOpenedClassName={triggerOpenedClassName}
      triggerDisabled={triggerDisabled}
      open={open}
    >
      {content}
    </Collapsible>
  );
}

function Trigger({ name, checkEnabled }) {
  return (
    <div className="ml-auto">
      <div className="trigger-div-style">
        {name}
        {checkEnabled && (
          <FontAwesomeIcon
            icon={faCheck}
            color="green"
            className="fa-xs enabled-style"
          />
        )}
      </div>
    </div>
  );
}

CollapsibleForm.propTypes = forbidExtraProps({
  trigger: PropTypes.oneOfType([PropTypes.element, PropTypes.string])
    .isRequired,
  triggerClassName: PropTypes.string.isRequired,
  triggerOpenedClassName: PropTypes.string.isRequired,
  triggerDisabled: PropTypes.bool,
  open: PropTypes.bool,
  content: PropTypes.oneOfType([PropTypes.element, PropTypes.string])
    .isRequired,
});

CollapsibleForm.defaultProps = {
  triggerDisabled: false,
  open: true,
};

Trigger.propTypes = forbidExtraProps({
  name: PropTypes.string.isRequired,
  checkEnabled: PropTypes.bool,
});

Trigger.defaultProps = {
  checkEnabled: false,
};

export { Trigger, CollapsibleForm };
