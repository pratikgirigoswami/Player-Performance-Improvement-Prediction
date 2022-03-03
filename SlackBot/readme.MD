## Instructions to run the server
1. Run ngrok.exe (via terminal rgrok.exe http 5000)
1. Run the .py code
1. Copy the Forwarding address
1. Include at the end of the address the endpoint (in this case /slack/events)
1. Go to Events Subscriptions in Slack Api page
1. Update the Request URL using this full address
1. Update the commands, at the Slash Commands section with the address (changing the endpoint to /slack/echo)