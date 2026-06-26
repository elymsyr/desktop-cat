// Pushes the current tab list to catyhoo's local receiver (providers.py, :8766).
// An MV3 service worker can only fetch outbound, so we PUSH on every tab change;
// catyhoo holds the latest snapshot and reads it in ChromeProvider.detect().
const ENDPOINT = "http://localhost:8766/tabs";

let timer = null;
function pushSoon() {
  // debounce: a burst of tab events (e.g. opening a window) -> one POST
  clearTimeout(timer);
  timer = setTimeout(push, 500);
}

async function push() {
  const tabs = await chrome.tabs.query({});
  const body = JSON.stringify(tabs.map(t => ({ title: t.title, url: t.url })));
  try {
    await fetch(ENDPOINT, { method: "POST", body });
  } catch (e) {
    // catyhoo not running -> nothing to push to; ignore until it is.
  }
}

chrome.runtime.onInstalled.addListener(pushSoon);
chrome.runtime.onStartup.addListener(pushSoon);
chrome.tabs.onCreated.addListener(pushSoon);
chrome.tabs.onRemoved.addListener(pushSoon);
chrome.tabs.onUpdated.addListener(pushSoon);
chrome.tabs.onActivated.addListener(pushSoon);

// Heartbeat: tab events alone go quiet if you don't touch Chrome, which would
// make catyhoo think Chrome closed. A 1-min alarm keeps the snapshot fresh.
chrome.alarms.create("heartbeat", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener(push);
