# build image from base image
FROM gmirror/{{cookiecutter.project_name}}-base:latest

# copy code
WORKDIR /app
COPY . .

# use `CMD` to avoid run command during docker build
CMD PROJECT_ENV=test nosetests -v --with-xunit --xunit-file=nosetests.xml --cover-package={{cookiecutter.project_slug}}--with-xcoverage