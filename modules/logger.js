const log4js = require('log4js');

const LOG_PATH = 'log';

log4js.configure("config/log4js.json");

module.exports = {
    application: log4js.getLogger('application'),
    express: log4js.connectLogger(log4js.getLogger('application'), {level: log4js.levels.ALL})
};
