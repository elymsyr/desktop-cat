import pychrome

# Define a callback function to handle events
def callback(message, **kwargs):
    if message.get('method') == 'Network.requestWillBeSent':
        request = message.get('params', {}).get('request', {})
        print("Request URL:", request.get('url'))

# Create a new instance of the Chrome class
chrome = pychrome.Browser()

# Connect to the Chrome instance
tab = chrome.new_tab()

# Enable network events so we can capture requests
tab.start()
tab.call_method('Network.enable')

# Set up the event listener
tab.set_listener(callback)

# Navigate to a webpage (you can replace this URL with any other)
tab.Page.navigate(url="https://www.example.com")

# Wait for the page to load (you can implement a more sophisticated wait strategy if needed)
tab.wait(5)

# Stop the tab (this will close the page)
tab.stop()

# Close the tab
chrome.close_tab(tab)

# Close the Chrome instance
chrome.close_browser()
