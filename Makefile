export REGISTRY ?=registry.gitlab.com
export RELEASE_REMOTE ?=pigroupe

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf ($$1 ~ "--" ? $$2 "\n" : "\033[36m%-10s \033[34m%s\033[0m\n", $$1,  $$2)}'
.DEFAULT_GOAL := help

startstackdev:
	cd developer-stack/swarm && vagrant up

install-semver: ## Install Semver package wit gem installer (https://github.com/flazz/semver/)
install-semver:
	@(sudo gem install semver) || true

#   make tag VERSION=(major|minor|patch)
tag: ## Publish new release.
tag: install-semver
	@semver inc $(VERSION)
	@echo "New release: `semver tag`"
	@echo Releasing sources
	@sed -i -r "s/version='([0-9]+\.[0-9]+\.[0-9]+)/version='`semver tag`/g" sentinel/setup.py
	@sed -i -r "s/version='v/version='/g" sentinel/setup.py
	@sed -i -r "s/sentinel:([0-9]+\.[0-9]+\.[0-9]+)/sentinel:`semver tag`/g" README.md
	@sed -i -r "s/sentinel:v/sentinel:/g" README.md

build-sentinel: ## Build docker image of last version of sentinel and push it in the ${REGISTRY} registry
build-sentinel:
	docker build -t ${REGISTRY}/pi-microservice/sentinel:`semver tag` .
	(docker push ${REGISTRY}/pi-microservice/sentinel:`semver tag`) || true

release: ## Tag git with last release
release:
	@git add .
	@(git commit -m "releasing `semver tag`") || true
	@(git tag --delete `semver tag`) || true
	@(git push --delete ${RELEASE_REMOTE} `semver tag`) || true
	@git tag `semver tag`
	@git push ${RELEASE_REMOTE} `semver tag`
	@GIT_CB=$(git symbolic-ref --short HEAD) && git push -u ${RELEASE_REMOTE} $(GIT_CB)
	@make -s build-sentinel

quality:
	./quality_wrapper
