import { createBadge } from '../utils/dashboard';

function NodeBadges({ node }) {
  let syncingBadge = null;
  let activeBadge = null;
  let disabledBadge = null;
  let electedBadge = null;
  let councilMemberBadge = null;
  if (node.isSyncing !== -1) {
    syncingBadge = node.isSyncing
      ? createBadge('Syncing', 'warning', 'Syncing')
      : createBadge('Synced', 'success', 'Synced');
  }
  const badges = [
    node.isDown ? createBadge('Down', 'danger', 'Down')
      : createBadge('Up', 'success', 'Up'),
    syncingBadge,
  ];
  if (node.isValidator) {
    if (node.isActive !== -1) {
      activeBadge = node.isActive ? createBadge('Active', 'success', 'Active')
        : createBadge('Inactive', 'danger', 'Inactive');
    }
    if (node.isDisabled !== -1) {
      disabledBadge = node.isDisabled
        ? createBadge('Disabled', 'danger', 'Disabled')
        : createBadge('Enabled', 'success', 'Enabled');
    }
    if (node.isElected !== -1) {
      electedBadge = node.isElected
        ? createBadge('Elected', 'success', 'Elected')
        : createBadge('Not Elected', 'warning', 'Not Elected');
    }
    if (node.isCouncilMember !== -1) {
      councilMemberBadge = node.isCouncilMember
        && createBadge('Council Member', 'primary', 'Council Member');
    }
    badges.push(activeBadge, disabledBadge, electedBadge, councilMemberBadge);
  }
  return badges;
}

export default NodeBadges;
