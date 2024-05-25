window.addEventListener('DOMContentLoaded', () => {
  chrome.tabs.query({}, (tabs) => {
    const tabsList = document.getElementById('tabsList');
    tabs.forEach(tab => {
      const li = document.createElement('li');
      const title = document.createElement('div');
      const url = document.createElement('div');
      
      title.textContent = `Title: ${tab.title}`;
      url.textContent = `URL: ${tab.url}`;
      
      li.appendChild(title);
      li.appendChild(url);
      tabsList.appendChild(li);
    });
  });
});
