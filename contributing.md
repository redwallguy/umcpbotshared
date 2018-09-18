
#How to contribute
So you want to contribute to UMCPBot? Great! Before you get started make sure you read through these guidelines.
## Getting Started
1. Fork the repo.
2. Then clone the repo: `git clone git@github.com:your-username/umcpbotshared.git`
3. Register a bot instance with the [Discord API](https://discordapp.com/developers/docs/intro "Discord API") (You will need this to test your changes).
4. Initialize a [PostgreSQL](https://www.postgresql.org/). server
5. Initialize a [Redis](https://redis.io) server.
5. Initialize your environment:
	The following environment variables need to be set:
	- `DISC_TOKEN` = your Discord API Token
	- `DATABASE_URL` = the connection url for your PostgreSQL server
	- `REDIS_URL` = the connection url for your Redis server
	- `WEBHOOK_URL` = the url for your discord channel webhook
 ## Contributing
Once you are all set up, start making changes! A good place to look for what you could help with is our [issues page](https://github.com/redwallguy/umcpbotshared/issues). If you instead plan to work on new functionality, please create a new issue first.
 After you are done with your code, push it to your fork and submit a [pull request](https://github.com/redwallguy/umcpbotshared/pull/new/exp)! When submitting, make sure you [reference which issue the pull request is for](https://blog.github.com/2013-05-14-closing-issues-via-pull-requests/). All pull requests should be done into the exp branch, as this is our active development branch.
