NAME := bsolid
ROOT := /var/www/bsolid

SSH_HOST := spurio.supervacuo.com
SSH_USER := admin

# SSH_OPTS := -q -o ControlMaster=auto -o ControlPath=.ssh-deployment.sock -o ControlPersist=2m
SSH_OPTS := -q

RELEASE != echo "$(NAME)-`git describe --always`"

deploy: /tmp/$(RELEASE) upload extract clean pip migrate link restart

/tmp/$(RELEASE):
	@ tput setaf 5; tput bold; echo "Generating '$(RELEASE).tar.gz'"; tput sgr0
	git-archive-all /tmp/$(RELEASE).tar.gz

upload:
	@ tput setaf 5; tput bold; echo "Uploading '$(RELEASE).tar.gz'"; tput sgr0
	scp /tmp/$(RELEASE).tar.gz $(SSH_USER)@$(SSH_HOST):/tmp/

extract:
	@ tput setaf 5; tput bold; echo "Extracting '$(RELEASE).tar.gz'"; tput sgr0
	@ ssh -t $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "cd $(ROOT) && sudo -u bsolid tar -xzf /tmp/$(RELEASE).tar.gz"

clean:
	@ rm /tmp/$(RELEASE).tar.gz
	@ ssh $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "rm /tmp/$(RELEASE).tar.gz"

pip:
	@ tput setaf 5; tput bold; echo "Installing pip requirements"; tput sgr0
	@ ssh -t $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "sudo -u bsolid $(ROOT)/venv/bin/pip install -r $(ROOT)/$(RELEASE)/requirements.txt"

migrate:
	@ tput setaf 5; tput bold; echo "Migrating database"; tput sgr0
	ssh -t $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "sudo -u bsolid FLASK_CONFIG='../../config_staging.py' $(ROOT)/venv/bin/python $(ROOT)/$(RELEASE)/app.py db -m"

link:
	@ tput setaf 5; tput bold; echo "Updating release symlink"; tput sgr0
	ssh -t $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "sudo -u bsolid sh -c 'rm -f $(ROOT)/previous && mv $(ROOT)/current $(ROOT)/previous || true && ln -s $(RELEASE) $(ROOT)/current'"

restart:
	@ tput setaf 5; tput bold; echo "Restarting gunicorn server"; tput sgr0
	ssh -t $(SSH_OPTS) $(SSH_USER)@$(SSH_HOST) "sudo systemctl restart bsolid.service"

.PHONY : deploy archive upload clean extract pip migrate link restart
