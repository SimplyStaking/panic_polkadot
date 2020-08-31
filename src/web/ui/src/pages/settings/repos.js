import React, { Component } from 'react';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import { ToastsStore } from 'react-toasts';
import { reposConfig } from '../../utils/templates';
import { getConfig } from '../../utils/data';
import {
  fieldEmpty,
  fieldValueUniqueAmongAllfieldsInJSON,
  fixSpecificSectionsOfConfig,
  highestItemIndexInConfig,
  keepSpecificSectionsFromConfig,
} from '../../utils/configs';
import { toBool } from '../../utils/string';
import { RemoveButton, SaveConfigButton } from '../../components/buttons';
import { REPO_CONFIG_TYPE } from '../../utils/constants';
import Page from '../../components/page';
import AddGitHubRepoForm from '../../components/forms/add_github_repo_form';
import '../../style/style.css';
import { generateAddedTableValues } from '../../utils/forms';

function GitHubReposTableContent({ reposConfigJson, handleRemoveRepo }) {
  const content = [];
  const repos = reposConfigJson;
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
        {generateAddedTableValues(data.repo_name, false)}
        {generateAddedTableValues(data.repo_page, false)}
        {generateAddedTableValues(data.monitor_repo, true)}
        <td>
          <RemoveButton
            itemKey={parseInt(repo.substr(repo.indexOf('_') + 1, repo.length),
              10)}
            handleRemove={handleRemoveRepo}
          />
        </td>
      </tr>,
    );
  });

  return content;
}

function ReposTable({ reposConfigJson, handleRemoveRepo }) {
  return (
    <div>
      <h1 className="heading-style-1" style={{ marginBottom: '-10px' }}>
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

function ReposConfig({
  handleAddRepo, handleChangeInNonBooleanField, handleChangeInBooleanField,
  currentRepoConfig, validated, repoNameValid, repoPageValid, reposConfigJson,
  handleRemoveRepo,
}) {
  return (
    <Container>
      <AddGitHubRepoForm
        handleAddRepo={handleAddRepo}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
        currentRepoConfig={currentRepoConfig}
        validated={validated}
        repoNameValid={() => repoNameValid()}
        repoPageValid={() => repoPageValid()}
      />
      <ReposTable
        reposConfigJson={reposConfigJson}
        handleRemoveRepo={handleRemoveRepo}
      />
      <SaveConfigButton
        configName="user_config_repos.ini"
        config={reposConfigJson}
      />
    </Container>
  );
}

class ReposSettingsPage extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get data periodically until the
    // data is fetched. This must be done since data from the config must be
    // fetched once.
    this.dataTimer = null;
    this.state = {
      reposConfigJson: {},
      currentRepoConfig: Object.create(
        reposConfig, Object.getOwnPropertyDescriptors(reposConfig),
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

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    this.dataTimer = null;
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
        response.data.result, reposConfig, 'repo_',
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
          reposConfig, Object.getOwnPropertyDescriptors(reposConfig),
        ),
        currentRepoIndex: prevState.currentRepoIndex + 1,
        validated: false,
      };
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

  handleChangeInNonBooleanField(event, field) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentRepoConfig;
      newConfig[field] = event.target.value;
      return { currentRepoConfig: newConfig };
    });
  }

  handleChangeInBooleanField(event, field) {
    this.setState((prevState) => {
      const newConfig = prevState.currentRepoConfig;
      newConfig[field] = (!toBool(prevState.currentRepoConfig[field]))
        .toString();
      return { currentRepoConfig: newConfig };
    });
  }

  render() {
    const { state } = this;
    return (
      <Page
        spinnerCondition={state.isFetchingData}
        component={(
          <ReposConfig
            handleAddRepo={repo => this.handleAddRepo(repo)}
            handleRemoveRepo={index => this.handleRemoveRepo(index)}
            currentRepoConfig={state.currentRepoConfig}
            reposConfigJson={state.reposConfigJson}
            validated={state.validated}
            handleChangeInNonBooleanField={
              (event, field) => {
                this.handleChangeInNonBooleanField(event, field);
              }
            }
            handleChangeInBooleanField={
              (event, field) => {
                this.handleChangeInBooleanField(event, field);
              }
            }
            repoNameValid={() => this.repoNameValid()}
            repoPageValid={() => this.repoPageValid()}
          />
        )}
      />
    );
  }
}

ReposConfig.propTypes = forbidExtraProps({
  handleAddRepo: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  currentRepoConfig: REPO_CONFIG_TYPE.isRequired,
  validated: PropTypes.bool.isRequired,
  repoNameValid: PropTypes.func.isRequired,
  repoPageValid: PropTypes.func.isRequired,
  reposConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  handleRemoveRepo: PropTypes.func.isRequired,
});

ReposTable.propTypes = forbidExtraProps({
  reposConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  handleRemoveRepo: PropTypes.func.isRequired,
});

export default ReposSettingsPage;
