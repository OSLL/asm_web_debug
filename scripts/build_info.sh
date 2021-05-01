DEBUG_FILE='./DEBUG'

COMMIT=$(git rev-parse HEAD)
COMMIT_MSG=$(git log --format=%B -n 1 $COMMIT)
BRANCH=$(git status |head -1| cut -d' ' -f 3)
DATE=$(date -R)
VERSION=$(git tag | tail -1)
[ ${#VERSION} == 0 ] && VERSION="no version" 
echo "commit=$COMMIT" > $DEBUG_FILE
message=$(echo "$COMMIT_MSG" | sed ':a; N; $!ba; s/\n/ /g')
echo -e "message=$message" >> $DEBUG_FILE
echo "date=$DATE" >> $DEBUG_FILE
echo "branch=$BRANCH" >> $DEBUG_FILE
echo "version=$VERSION" >> $DEBUG_FILE