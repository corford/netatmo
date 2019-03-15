import wretch from 'wretch';

export class Sandbox {
  constructor() {

    document.getElementById('sandbox-test-auth').addEventListener('click', event => {
      this._grant(this._getServer(), this._getJWT());
    });

    document.getElementById('sandbox-test-list').addEventListener('click', event => {
      this._getDevices(this._getServer(), this._getJWT());
    });

    document.getElementById('sandbox-test-station-device-dashboard-data').addEventListener('click', event => {
      this._getStationDeviceDashboardData(this._getServer(), this._getJWT());
    });

    document.getElementById('sandbox-test-home-timezone').addEventListener('click', event => {
      this._getHomeTimezone(this._getServer(), this._getJWT());
    });

    document.getElementById('sandbox-test-revoke').addEventListener('click', event => {
      this._revokeAccess(this._getServer(), this._getJWT());
    });

    document.getElementById('sandbox-clear').addEventListener('click', event => {
      this._clearLog();
    });
  }

  _getServer() {
    const server = document.getElementById('sandbox-server').value;
    return (server.length > 0 ) ? server : 'http://127.0.0.1:5000';
  }

  _getJWT() {
    return document.getElementById('sandbox-jwt').value;
  }

  _grant(server, jwt) {
    this._log(`request access`);
    window.open(`${server}/auth/grant?jwt=${jwt}`, 'sandbox-grant');
  }

  _getDevices(server, jwt) {
    this._showLoader();
    this._log(`request devices`);

    wretch(`${server}/api/devices/v1/list`)
    .auth(`Bearer ${jwt}`)
    .get()
    .json(json => {
      this._log(JSON.stringify(json));
    })
  
    this._hideLoader();
  }

  _getStationDeviceDashboardData(server, jwt) {
    this._showLoader();

    const device_id = document.getElementById('sandbox-station-device-id').value;
    this._log(`get dashboard data for station device: ${device_id}`);

    wretch(`${server}/api/station/v1/dashboard-data`)
    .auth(`Bearer ${jwt}`)
    .query({'device_id': device_id})
    .get()
    .json(json => {
      this._log(JSON.stringify(json));
    })

    this._hideLoader();
  }
  
  _getHomeTimezone(server, jwt) {
    this._showLoader();

    const home_id = document.getElementById('sandbox-station-home-id').value;
    this._log(`get timezone data for home: ${home_id}`);

    wretch(`${server}/api/home/v1/timezone`)
    .auth(`Bearer ${jwt}`)
    .query({'home_id': home_id})
    .get()
    .json(json => {
      this._log(JSON.stringify(json));
    })

    this._hideLoader();
  }
  
  _revokeAccess(server, jwt) {
    this._showLoader();
    this._log(`revoke access`);

    this._hideLoader();
  }

  _log(msg) {
    const today = new Date();
    const time = ("0" + today.getHours()).slice(-2) + ":" + today.getMinutes() + ":" + today.getSeconds();
    const log = document.getElementById('sandbox-log');
    log.value = log.value + `[${time}] ${msg}\n`;
  }

  _clearLog() {
    console.log(`clearing log`);
    document.getElementById('sandbox-log').value = '';
  }  

  _showLoader() {
    document.getElementById('sandbox-server').classList.add('is-loading');
  }

  _hideLoader() {
    document.getElementById('sandbox-server').classList.remove('is-loading');
  }
}


export default function () {
  const sandbox = new Sandbox();
}
