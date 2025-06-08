APP_NAME = NFT
PRISMA_SCHEME = ./schema.prisma

target:
	@awk -F ':|##' '/^[^\t].+?:.*?##/ { printf "\033[0;36m%-15s\033[0m %s\n", $$1, $$NF }' $(MAKEFILE_LIST)

git_pull:  ## Pull the latest code from git
	git pull

pm2_start:  ## Create a PM2 instance
	pm2 start uv --name $(APP_NAME) --interpreter none -- run index.py -u

pm2_restart:  ## Restart PM2
	pm2 restart $(APP_NAME)

update: git_pull pm2_restart  ## Pull and reboot PM2
