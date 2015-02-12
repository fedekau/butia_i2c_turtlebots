#!/bin/sh

changelog_file=ChangeLog
latest_tag=$(git describe --tags --abbrev=0)

git log --pretty='format:Author: %an%n%w(0,4,4)%B' $latest_tag..HEAD > $changelog_file
