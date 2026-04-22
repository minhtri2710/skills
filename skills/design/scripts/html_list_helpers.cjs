function getDirectChildListItems(element) {
  return Array.from(element?.children || []).filter((child) => child?.tagName === 'LI');
}

module.exports = {
  getDirectChildListItems,
};
