import json
import sys

def get_tabs():
    tabs = []
    for line in sys.stdin:
        message = json.loads(line)
        if message["action"] == "getTabs":
            for tab in message["tabs"]:
                tabs.append({"title": tab["title"], "url": tab["url"]})
            break
    return tabs

def send_response(response):
    sys.stdout.write(json.dumps(response))
    sys.stdout.flush()

if __name__ == "__main__":
    tabs = get_tabs()
    response = {"tabs": tabs}
    send_response(response)
