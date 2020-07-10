import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { fieldEmpty } from '../../utils/configs';
import { REPO_CONFIG_TYPE } from '../../utils/constants';
import { toBool } from '../../utils/string';
import {
  createColumnFormContentWithSubmit,
  createColumnWithContent,
  createFormLabel,
} from '../../utils/forms';
import TooltipOverlay from '../overlays';
import { PingRepoButton } from '../buttons';
import { CollapsibleForm, Trigger } from './collapsible_form';
import '../../style/style.css';

function AddGitHubRepoForm({
  handleAddRepo, handleChangeInNonBooleanField, handleChangeInBooleanField,
  currentRepoConfig, validated, repoNameValid, repoPageValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Name'),
    createFormLabel(true, '3', 'Page'),
    createFormLabel(true, '3', 'Monitor repo'),
  ];
  const columns = [
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={
              event => handleChangeInNonBooleanField(event, 'repo_name')
            }
            value={currentRepoConfig.repo_name}
            placeholder="Polkadot"
            isInvalid={validated && !repoNameValid()}
            isValid={validated && repoNameValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(currentRepoConfig.repo_name)
            ? (
              <Form.Control.Feedback type="invalid">
                Repo name cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Repo names must be unique
              </Form.Control.Feedback>
            )}
        </div>,
        1,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <TooltipOverlay
            identifier="repo-name-info"
            placement="right"
            tooltipText={'Any name which helps you identify the repo. '
          + 'Must be unique'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
        </div>,
        2,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={
              event => handleChangeInNonBooleanField(event, 'repo_page')
            }
            value={currentRepoConfig.repo_page}
            placeholder="paritytech/polkadot/"
            isInvalid={validated && !repoPageValid()}
            isValid={validated && repoPageValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(currentRepoConfig.repo_page)
            ? (
              <Form.Control.Feedback type="invalid">
                Repo page cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Repo page must end with &apos;/&apos;
              </Form.Control.Feedback>
            )}
          <Form.Text className="text-muted">
            Official GitHub repository. Format: w3f/substrate/
          </Form.Text>
        </div>,
        3,
      ),
      createColumnWithContent(
        '2',
        <div>
          <PingRepoButton
            disabled={!repoPageValid()}
            repo={currentRepoConfig.repo_page}
          />
        </div>,
        4,
      ),
    ],
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="monitor-repo-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={
              event => handleChangeInBooleanField(event, 'monitor_repo')
            }
            checked={toBool(currentRepoConfig.monitor_repo)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <TooltipOverlay
            identifier="monitor-repo"
            placement="right"
            tooltipText="Tick if you would like your repo to be monitored."
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
        </div>
      </div>,
      5,
    ),
  ];
  return (
    <div>
      <h1 className="heading-style-1">GitHub Repositories Configuration</h1>
      <div className="div-style">
        <CollapsibleForm
          trigger={(<Trigger name="GitHub Repo" />)}
          triggerClassName="collapsible-style"
          triggerOpenedClassName="collapsible-style"
          open
          content={(
            <div>
              <Form.Text className="text-muted info-div-style">
                The GitHub monitor alerts on new releases in repositories. If
                you would like a GitHub repo to be monitored, fill the form
                below and press &apos;Add Repo&apos;.
              </Form.Text>
              {createColumnFormContentWithSubmit(
                labels, columns, handleAddRepo, 'Add Repo',
              )}
            </div>
          )}
        />
      </div>
    </div>
  );
}

AddGitHubRepoForm.propTypes = forbidExtraProps({
  currentRepoConfig: REPO_CONFIG_TYPE.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleAddRepo: PropTypes.func.isRequired,
  validated: PropTypes.bool.isRequired,
  repoNameValid: PropTypes.func.isRequired,
  repoPageValid: PropTypes.func.isRequired,
});

export default AddGitHubRepoForm;
