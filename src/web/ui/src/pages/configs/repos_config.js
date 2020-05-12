import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Table from 'react-bootstrap/Table';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import Spinner from 'react-bootstrap/Spinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons/faTimesCircle';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import {
  ToastsContainer,
  ToastsContainerPosition,
  ToastsStore,
} from 'react-toasts';
import '../../style/style.css';
import {
  CollapsibleForm,
  createColumnWithContent,
  createFormLabel,
  Trigger,
} from './main_user_config';
import { repoConfig } from '../../utils/templates';
import { fetchData, getConfig, sendConfig } from '../../utils/data';
import {
  fieldEmpty,
  fieldValueUniqueAmongAllfieldsInJSON,
  fixSpecificSectionsOfConfig,
  highestItemIndexInConfig,
  keepSpecificSectionsFromConfig,
} from '../../utils/configs';
import { toBool } from '../../utils/string';
import { createColumnFormWithSubmit } from './nodes_config';

function pingRepo(url) {
  return fetchData(url);
}

function AddGitHubRepoForm({
  currentRepoConfig, handleChangeInRepoName, handleChangeInPage,
  handleChangeInMonitorRepoStatus, handleAddRepo, validated, repoNameValid,
  repoPageValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Name'), createFormLabel(true, '3', 'Page'),
    createFormLabel(true, '3', 'Monitor repo'),
  ];
  const columns = [
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={event => handleChangeInRepoName(event)}
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
          <OverlayTrigger
            key="repo-name-info-overlay"
            placement="right"
            overlay={(
              <Tooltip id="repo-name-info-tooltip">
                Any name which helps you identify the repo. Must be unique
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
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
            onChange={event => handleChangeInPage(event)}
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
          <Button
            className="button-style2"
            disabled={!repoPageValid()}
            onClick={async () => {
              try {
                ToastsStore.info(`Connecting with repo ${
                  currentRepoConfig.repo_page
                }`, 5000);
                // Remove last '/' to connect with
                // https://api.github.com/repos/repoPage`.
                const repoPage = currentRepoConfig.repo_page;
                await pingRepo(
                  `https://api.github.com/repos/${
                    repoPage.substring(0, repoPage.length - 1)
                  }`,
                );
                ToastsStore.success('Successfully connected', 5000);
              } catch (e) {
                if (e.response) {
                  // The request was made and the server responded
                  // with a status code that falls out of the
                  // range of 2xx
                  ToastsStore.error(
                    `Could not connect with repo ${
                      currentRepoConfig.repo_page
                    }. Error: ${e.response.data.message}`, 5000,
                  );
                } else {
                  // Something happened in setting up the request
                  // that triggered an Error
                  ToastsStore.error(
                    `Could not connect with repo ${
                      currentRepoConfig.repo_page
                    }. Error: ${e.message}`, 5000,
                  );
                }
              }
            }
            }
          >
            Connect with repo
          </Button>
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
            onChange={() => handleChangeInMonitorRepoStatus()}
            checked={toBool(currentRepoConfig.monitor_repo)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="monitor-repo-overlay"
            placement="right"
            overlay={(
              <Tooltip id="monitor-repo-tooltip">
                Tick if you would like your repo to be monitored.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      5,
    ),
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(<Trigger name="GitHub Repo" />)}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              The GitHub monitor alerts on new releases in repositories. If you
              would like a GitHub repo to be monitored, fill the form below and
              press &apos;Add Repo&apos;.
            </Form.Text>
            {createColumnFormWithSubmit(
              labels, columns, handleAddRepo, 'Add Repo',
            )}
          </div>
        )}
      />
    </div>
  );
}

function GitHubReposConfigForm({
  handleAddRepo, handleChangeInRepoName, handleChangeInPage,
  handleChangeInMonitorRepoStatus, currentRepoConfig, validated, repoNameValid,
  repoPageValid,
}) {
  return (
    <div>
      <h1 className="heading-style-1">GitHub Repositories Configuration</h1>
      <AddGitHubRepoForm
        handleAddRepo={handleAddRepo}
        handleChangeInRepoName={handleChangeInRepoName}
        handleChangeInPage={handleChangeInPage}
        handleChangeInMonitorRepoStatus={handleChangeInMonitorRepoStatus}
        currentRepoConfig={currentRepoConfig}
        validated={validated}
        repoNameValid={repoNameValid}
        repoPageValid={repoPageValid}
      />
    </div>
  );
}

function GitHubReposTableContent(props) {
  const content = [];
  const repos = props.reposConfigJson;

  if (Object.keys(repos).length === 0) {
    content.push(
      <tr key="no-content-key">
        <td colSpan="4" className="date-style">
          No GitHub repos for monitoring added yet! Use the form above to add
          GitHub repos.
        </td>
      </tr>,
    );
    return content;
  }

  Object.entries(repos).forEach(([repo, data]) => {
    content.push(
      <tr key={repo}>
        {fieldEmpty(data.repo_name) ? <td>N/a</td> : <td>{data.repo_name}</td>}
        {fieldEmpty(data.repo_page) ? <td>N/a</td> : <td>{data.repo_page}</td>}
        <td className="column-style">
          {
            toBool(data.monitor_repo) ? (
              <FontAwesomeIcon icon={faCheck} color="green" />
            ) : (<FontAwesomeIcon icon={faTimes} color="red" />)
          }
        </td>
        <td>
          <button
            className="delete-button-style"
            onClick={() => props.handleRemoveRepo(parseInt(repo.substr(
              repo.length - 1,
            ), 10))}
            type="button"
          >
            <FontAwesomeIcon
              icon={faTimesCircle}
              color="red"
              className="fa-remove"
            />
          </button>
        </td>
      </tr>,
    );
  });

  return content;
}

function GitHubReposTable({ reposConfigJson, handleRemoveRepo }) {
  return (
    <div>
      <h1 className="heading-style-2" style={{ marginBottom: '-10px' }}>
        Added Repos
      </h1>
      <Table responsive className="tables-style">
        <thead>
          <tr>
            <th>Name</th>
            <th>Page</th>
            <th className="column-style">Monitor Repo</th>
            <th>{}</th>
          </tr>
        </thead>
        <tbody>
          <GitHubReposTableContent
            reposConfigJson={reposConfigJson}
            handleRemoveRepo={handleRemoveRepo}
          />
        </tbody>
      </Table>
    </div>
  );
}

class ReposConfig extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get the data periodically until the
    // data is fetched. This must be done since data from the config must be
    // fetched once.
    this.dataTimer = null;
    this.state = {
      reposConfigJson: {},
      currentRepoConfig: Object.create(
        repoConfig, Object.getOwnPropertyDescriptors(repoConfig),
      ),
      isFetchingData: true,
      currentRepoIndex: 0,
      validated: false,
    };
  }

  componentDidMount() {
    this.fetchReposConfig();
    this.dataTimer = setInterval(this.fetchReposConfig.bind(this), 5000);
  }

  async fetchReposConfig() {
    let response;
    try {
      response = await getConfig('user_config_repos.ini');
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded
        // with a status code that falls out of the range of
        // 2xx
        ToastsStore.error(
          `Error: ${e.response.data.error}`, 5000,
        );
      } else {
        // Something happened in setting up the request that
        // triggered an Error
        ToastsStore.error(`Error: ${e.message}`, 5000);
      }
      return;
    }
    const reposConfigJson = response.data.result;
    // Remove timer since data was obtained
    clearInterval(this.dataTimer);
    this.dataTimer = null;
    if (reposConfigJson !== undefined
      && Object.keys(reposConfigJson).length !== 0) {
      // Since we need to store repos in the config under the section 'repo_i',
      // the current index must always be one greater than the highest i in
      // 'repo_i' from the repos_config.
      const highestRepoIndex = highestItemIndexInConfig(
        reposConfigJson, 'repo_',
      );
      let checkedConfig = fixSpecificSectionsOfConfig(
        response.data.result, repoConfig, 'repo_',
      );
      checkedConfig = keepSpecificSectionsFromConfig(checkedConfig, 'repo_');
      this.setState({
        reposConfigJson: checkedConfig,
        isFetchingData: false,
        currentRepoIndex: highestRepoIndex + 1,
      });
    } else {
      this.setState({ isFetchingData: false });
    }
  }

  handleAddRepo(event) {
    // If the form has invalid input set the validation to true so that correct
    // and incorrect input fields can be displayed. If the form has valid inputs
    // save the input
    event.preventDefault();
    if (!this.repoDataValid()) {
      this.setState({ validated: true });
      event.stopPropagation();
      return;
    }
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const { reposConfigJson, currentRepoConfig } = prevState;
      const currentRepoIndex = prevState.currentRepoIndex.toString();
      reposConfigJson[`repo_${currentRepoIndex}`] = currentRepoConfig;
      return {
        reposConfigJson,
        currentRepoConfig: Object.create(
          repoConfig, Object.getOwnPropertyDescriptors(repoConfig),
        ),
        currentRepoIndex: prevState.currentRepoIndex + 1,
        validated: false,
      };
    });
  }

  repoNameValid() {
    const { state } = this;
    return !fieldEmpty(state.currentRepoConfig.repo_name)
      && fieldValueUniqueAmongAllfieldsInJSON(
        state.reposConfigJson, 'repo_name', state.currentRepoConfig.repo_name,
      );
  }

  repoPageValid() {
    const { currentRepoConfig } = this.state;
    return !fieldEmpty(currentRepoConfig.repo_page)
      && currentRepoConfig.repo_page.endsWith('/');
  }

  repoDataValid() {
    return this.repoNameValid() && this.repoPageValid();
  }

  handleChangeInRepoName(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentRepoConfig;
      newConfig.repo_name = event.target.value;
      return { currentRepoConfig: newConfig };
    });
  }

  handleChangeInPage(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentRepoConfig;
      newConfig.repo_page = event.target.value;
      return { currentRepoConfig: newConfig };
    });
  }

  handleChangeInMonitorRepoStatus() {
    this.setState((prevState) => {
      const newConfig = prevState.currentRepoConfig;
      newConfig.monitor_repo = (
        !toBool(prevState.currentRepoConfig.monitor_repo)
      ).toString();
      return { currentRepoConfig: newConfig };
    });
  }

  handleRemoveRepo(index) {
    this.setState((prevState) => {
      const updatedReposConfig = prevState.reposConfigJson;
      delete updatedReposConfig[`repo_${index}`];
      const highestRepoIndex = highestItemIndexInConfig(
        updatedReposConfig, 'repo_',
      );
      return {
        reposConfigJson: updatedReposConfig,
        currentRepoIndex: highestRepoIndex + 1,
      };
    });
  }

  render() {
    const { state } = this;
    return (
      <div>
        {
          state.isFetchingData
            ? (
              <div className="div-spinner-style">
                <Spinner
                  animation="border"
                  role="status"
                  className="spinner-style"
                />
              </div>
            )
            : (
              <Container>
                <GitHubReposConfigForm
                  handleAddRepo={repo => this.handleAddRepo(repo)}
                  handleChangeInRepoName={
                    event => this.handleChangeInRepoName(event)
                  }
                  handleChangeInPage={event => this.handleChangeInPage(event)}
                  handleChangeInMonitorRepoStatus={
                    () => this.handleChangeInMonitorRepoStatus()
                  }
                  currentRepoConfig={state.currentRepoConfig}
                  validated={state.validated}
                  repoNameValid={() => this.repoNameValid()}
                  repoPageValid={() => this.repoPageValid()}
                />
                <GitHubReposTable
                  reposConfigJson={state.reposConfigJson}
                  handleRemoveRepo={index => this.handleRemoveRepo(index)}
                />
                {
                  Object.keys(state.reposConfigJson).length > 0 && (
                    <div className="div-content-centre-style-margin-top">
                      <Button
                        className="button-style2"
                        onClick={async () => {
                          try {
                            ToastsStore.info('Saving config', 5000);
                            await sendConfig(
                              'user_config_repos.ini',
                              state.reposConfigJson,
                            );
                            ToastsStore.success('Config saved', 5000);
                          } catch (e) {
                            if (e.response) {
                              // The request was made and the server responded
                              // with a status code that falls out of the
                              // range of 2xx
                              ToastsStore.error(
                                `Saving failed. Error: ${
                                  e.response.data.error
                                }`, 5000,
                              );
                            } else {
                              // Something happened in setting up the request
                              // that triggered an Error
                              ToastsStore.error(
                                `Saving failed. Error: ${e.message}`, 5000,
                              );
                            }
                          }
                        }
                        }
                      >
                        Save Config
                      </Button>
                    </div>
                  )
                }
              </Container>
            )
        }
        <ToastsContainer
          store={ToastsStore}
          position={ToastsContainerPosition.TOP_CENTER}
          lightBackground
        />
      </div>
    );
  }
}

const repoConfigType = PropTypes.shape({
  repo_name: PropTypes.string,
  repo_page: PropTypes.string,
  monitor_repo: PropTypes.string,
});

AddGitHubRepoForm.propTypes = forbidExtraProps({
  currentRepoConfig: repoConfigType.isRequired,
  handleChangeInRepoName: PropTypes.func.isRequired,
  handleChangeInPage: PropTypes.func.isRequired,
  handleChangeInMonitorRepoStatus: PropTypes.func.isRequired,
  handleAddRepo: PropTypes.func.isRequired,
  validated: PropTypes.bool.isRequired,
  repoNameValid: PropTypes.func.isRequired,
  repoPageValid: PropTypes.func.isRequired,
});

GitHubReposConfigForm.propTypes = forbidExtraProps({
  currentRepoConfig: repoConfigType.isRequired,
  handleChangeInRepoName: PropTypes.func.isRequired,
  handleChangeInPage: PropTypes.func.isRequired,
  handleChangeInMonitorRepoStatus: PropTypes.func.isRequired,
  handleAddRepo: PropTypes.func.isRequired,
  validated: PropTypes.bool.isRequired,
  repoNameValid: PropTypes.func.isRequired,
  repoPageValid: PropTypes.func.isRequired,
});

GitHubReposTable.propTypes = forbidExtraProps({
  reposConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  handleRemoveRepo: PropTypes.func.isRequired,
});

export default ReposConfig;

// TODO: Save button do component on its own
