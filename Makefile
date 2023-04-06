target:
	@echo hello world lol

update:
	git pull
	pm2 restart pm2.json
