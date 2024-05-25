chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.query({}, (tabs) => {
    const tabURLs = tabs.map(tab => tab.url);
    console.log(tabURLs);
    // You can perform any action with the list of tab URLs here
  });
});
