const assert = require('assert');

module.exports = {
  findDocuments: (db, colName, query, callback) => {
    const collection = db.collection(colName);
    collection.countDocuments({}, (err, totalCount) => {
      assert.equal(err, null);
      collection.find({}, query)
        .toArray((err, docs) => {
          assert.equal(err, null);
          callback(totalCount, docs);
        });
    });
  },

  options: {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    socketTimeoutMS: 10000,
    connectTimeoutMS: 10000,
    serverSelectionTimeoutMS: 5000,
  },

  blankReturn: {
    total_pages: 0,
    alerts: [],
  },
};
