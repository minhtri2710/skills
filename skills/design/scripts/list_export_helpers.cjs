function decorateListRuns({ listTagName, index, textIndent, runs }) {
  const manualBulletPrefix = /^[•\-\*▪▸]\s*/;
  const normalizedTagName = String(listTagName || '').toUpperCase();
  const nextRuns = Array.isArray(runs)
    ? runs.map((run) => ({
        ...run,
        options: { ...(run?.options || {}) },
      }))
    : [];

  if (nextRuns.length === 0) {
    return nextRuns;
  }

  nextRuns[0].text = String(nextRuns[0].text || '').replace(manualBulletPrefix, '');

  if (normalizedTagName === 'OL') {
    nextRuns[0].text = `${index + 1}. ${nextRuns[0].text}`;
    delete nextRuns[0].options.bullet;
    return nextRuns;
  }

  nextRuns[0].options.bullet = { indent: textIndent };
  return nextRuns;
}

module.exports = {
  decorateListRuns,
};
