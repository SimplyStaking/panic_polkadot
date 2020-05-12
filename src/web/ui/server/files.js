const fs = require('fs');
const md5 = require('md5');
const path = require('path');

module.exports = {
  listenFileChanges: (file, uponChange, uponDeleted) => {
    let md5Previous = null;
    const fileDir = path.dirname(file); // path excl. filename
    const fileName = path.basename(file); // filename excl. path

    // Watch file for content changes (also reports if file deleted)
    fs.watch(fileDir, (event, who) => {
      if (who === fileName) {
        if (fs.existsSync(file)) {
          const md5Current = md5(fs.readFileSync(file));
          if (md5Current === md5Previous) {
            return; // no change if same content
          }
          console.log('Change detected in %s', file);
          md5Previous = md5Current;
          uponChange();
        } else {
          console.log('Change detected in %s but '
            + 'file not found (deleted?)', file);
          uponDeleted();
        }
      }
    });
  },
};
