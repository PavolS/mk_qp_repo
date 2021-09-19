#!/usr/bin/env bash

set -eux

MYDIR=$(greadlink -f $(dirname $0))

source $MYDIR/config.env

echo $MYDIR $VERSION

gh auth status || exit 1

gh repo view lotum/$TARGET_NAME 2> /dev/null && \
    echo -e "Please delete $TARGET_NAME: gh api -X DELETE repos/lotum/$TARGET_NAME\n(You may need: gh auth refresh -h github.com -s delete_repo)" && exit 1

mkdir -p $MY_TEMP_DIR && cd $MY_TEMP_DIR || exit 10
#trap "rm -rf $MY_TEMP_DIR" EXIT


git init || exit 2
echo -e "###$TARGET_NAME\n\n$DESCRIPTION" > README.md
git add . && git commit -m "Add readme." || exit 2

git subtree add --prefix $BACKEND_NAME $BACKEND_REPO master || exit 2

#git subtree add --prefix $CLIENT_NAME $CLIENT_REPO master || exit 2

git subtree add --prefix $PAGE_NAME $PAGE_REPO master || exit 2

$MYDIR/merge_workflows.py $MY_TEMP_DIR $BACKEND_NAME $PAGE_NAME || exit 3

gh repo create lotum/$TARGET_NAME --private --description "$DESCRIPTION" --confirm || exit 1

git push --set-upstream origin master || exit 2

gh repo view lotum/$TARGET_NAME  || exit 1

