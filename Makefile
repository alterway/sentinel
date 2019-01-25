export REGISTRY ?=hub.alterway.fr
export RELEASE_REMOTE ?=origin

startstackdev:
	cd developer-stack/swarm && vagrant up

install-semver:
	@(sudo gem install semver) || true

# Publish new release. Usage:
#   make tag VERSION=(major|minor|patch)
tag: install-semver
	@semver inc $(VERSION)
	@echo "New release: `semver tag`"
	@echo Releasing sources
	@sed -i -r "s/version='([0-9]+\.[0-9]+\.[0-9]+)/version='`semver tag`/g" sentinel/setup.py
	@sed -i -r "s/version='v/version='/g" sentinel/setup.py
	@sed -i -r "s/sentinel:([0-9]+\.[0-9]+\.[0-9]+)/sentinel:`semver tag`/g" README.md
	@sed -i -r "s/sentinel:v/sentinel:/g" README.md

build-sentinel:
	docker build -t ${REGISTRY}/sentinel:`semver tag` .
	(docker push ${REGISTRY}/sentinel:`semver tag`) || true

# Tag git with last release
release:
	@git add .
	@(git commit -m "releasing `semver tag`") || true
	@(git tag --delete `semver tag`) || true
	@(git push --delete origin `semver tag`) || true
	@git tag `semver tag`
	@git push origin `semver tag`
	@GIT_CB=$(git symbolic-ref --short HEAD) && git push -u ${RELEASE_REMOTE} $(GIT_CB)
	@make -s build-sentinel

quality:
	./quality_wrapper
