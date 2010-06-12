#!/bin/bash
# Tag an SVN project, ie copy from the current "thunk" to the tags directory
# Copy the project directory from THUNK_DIR to TAG_DIR/release-$VERSION
# the log message is set to the string "Release $VERSION"
# From http://dafizilla.wordpress.com/2007/08/20/script-to-tag-svn-versions/
if [ $# -lt 1 ];
then
    echo $0 project_name tag_version_number
else
echo Tagging release $1

BASE_URL=https://pypub.svn.sourceforge.net/svnroot/pypub

echo svn cp $BASE_URL/trunk $BASE_URL/tags/release-$1 -m "Release $1"
svn cp $BASE_URL/trunk $BASE_URL/tags/release-$1 -m "Release $1"
fi
