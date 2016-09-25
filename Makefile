WEBPACK=./node_modules/.bin/webpack

.PHONY: all
all: build

.PHONY: build
build: build-js server/server.py

.PHONY: build-js
build-js:
ifeq ($(OPTIMIZE), 1)
	NODE_ENV=production $(WEBPACK) --bail
else
	$(WEBPACK) --bail
endif

.PHONY: run
run:
	cd server && ./app.py

.PHONY: run-gae
run-gae:
	cd server && dev_appserver.py --port 8080 .

.PHONY: watch
watch:
	$(WEBPACK) --progress --colors --watch

.PHONY: run-dev-server
run-dev-server:
	webpack-dev-server --inline --progress --colors -d --host 0.0.0.0 --port 8081

server/server.py: server/server.js
	python -c "import js2py; js2py.translate_file('$<', '$@')"

server/server.js: build-js

.PHONY: clean
clean:
	-rm -rf server/server.py server/server.js server/public/js/app.js

.PHONY: deps
deps:
	yarn
	pip install -r requirements.txt
	pip install --target server/vendor js2py

.PHONY: check-integration
check-integration:
	./node_modules/.bin/mocha --timeout 60000 --compilers js:babel-core/register Tests/Integration/**/*.js

.PHONY: run-webdriver
run-webdriver:
	./node_modules/.bin/phantomjs --webdriver=4444
