
#!/bin/bash
set -e

if [[ $(uname -a) == *"Microsoft"* ]]; then
  echo "Running on Windows"
else
  echo "Running on $(uname -a)"
  alias python=python3
  alias pip=pip3
fi

# if make_venv dir is not present, then make it
if [ ! -d "venv" ]; then
  ./install
fi
. ./venv/bin/activate


export IN_ACTIVATED_ENV="1"

set +e
