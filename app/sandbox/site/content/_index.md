---
author: "Charlie Orford"
Sitemap:
  Priority: 1.0
---
<main>
  <section class="section">
    <div class="container">
      <h1 class="title is-4">Welcome to the Client API Sandbox</h1>
      <p class="is-size-9">Use it to test server endpoints and simulate an auth flow with Netatmo's upstream API.</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
    <div class="columns is-8 is-desktop">
      <div class="column is-4">
        <h4 class="title is-8">JWT Token</h4>
        <textarea id="sandbox-jwt" rows="10" class="textarea" placeholder="Paste your token here"></textarea><br>
        <p><strong>Why?</strong> Accessing the server API endpoints requires a token. During dev/testing, you can use a dummy token generated with the <span class="is-family-code">jwt-tools.sh</span> script (located in this project's <span class="is-family-code">devops/hack/</span> folder). Consult the README for more info.</p>
      </div>
      <div class="column is-3">
        <h4 class="title is-8">Available Tests</h4>
        <a id="sandbox-test-auth" class="button is-primary">Grant Netatmo access</a><br><br>
        <a id="sandbox-test-list" class="button is-primary">List devices</a><br><br>
        <a id="sandbox-test-station-device-dashboard-data" class="button is-primary">Get station dashboard data</a><br>
        <div class="field">
          <div class="control">
            <input id="sandbox-station-device-id" class="input" type="text" placeholder="Enter station id you wish to query" style="width: 300px;">
          </div>
        </div>
        <a id="sandbox-test-home-timezone" class="button is-primary">Get home timezone</a><br>
        <div class="field">
          <div class="control">
            <input id="sandbox-station-home-id" class="input" type="text" placeholder="Enter home id you wish to query" style="width: 300px;">
          </div>
        </div>
        <a id="sandbox-test-revoke" class="button is-danger">Revoke Netatmo access</a>
      </div>
      <div class="column is-5">
        <h4 class="title is-8">Activity Log</h4>
        <textarea id="sandbox-log" rows="10" class="textarea" placeholder="Results for each test will appear here"></textarea><br>
        <div class="field is-pulled-left">
          <div class="control">
            <input id="sandbox-server" class="input" type="text" placeholder="Server host (default: http://127.0.0.1:5000)" style="width: 400px;">
          </div>
        </div>
        <a id="sandbox-clear" class="button is-text is-pulled-right">Clear results</a>
      </div>
    </div>
    </div>
  </section>  
</main>
