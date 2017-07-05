#!/bin/bash
# Written by Suzhengchun on 20160213

set -e
BUILDDIR=build
rm -rf $BUILDDIR
if [ ! -f $BUILDDIR ]; then
    mkdir -p $BUILDDIR
fi
pushd $BUILDDIR
cmake ..
make VERBOSE=1 -j 1
cp `pwd`/lib/vnctpmd.so ../vnctpmd/test/vnctpmd.so
cp `pwd`/lib/vnctptd.so ../vnctptd/test/vnctptd.so
cp ../vnctpmd/test/vnctpmd.* ../../vanas_md/
cp ../vnctptd/test/vnctptd.* ../../vanas_td/
popd
