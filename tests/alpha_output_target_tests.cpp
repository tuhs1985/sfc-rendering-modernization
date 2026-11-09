#include "../tools/d3d9_proof/output_target.h"
#include <iostream>
#include <stdexcept>
int main(){unsigned checks=0;auto test=[&](bool value){if(!value)throw std::runtime_error("target notice");++checks;};
 output_target::Store store{};output_target::Notice n{},observed{};DWORD session[4]={1,2,3,4};
 test(!output_target::read(store,observed));n.pid=123;memcpy(n.session,session,16);n.observed=1;n.width=3840;n.height=2160;n.device=1;n.generation=1;
 output_target::publish(store,n);test(output_target::read(store,observed));test(output_target::valid(observed,session,123));
 test(!output_target::valid(observed,session,124));DWORD other[4]={1,2,3,5};test(!output_target::valid(observed,other,123));
 ++observed.width;test(!output_target::valid(observed,session,123));
 InterlockedIncrement(&store.sequence);test(!output_target::read(store,observed));InterlockedIncrement(&store.sequence);
 n.width=1031;n.height=517;++n.generation;output_target::publish(store,n);test(output_target::read(store,observed));test(output_target::valid(observed,session,123));test(observed.generation==2);
 n.width=0;output_target::publish(store,n);test(output_target::read(store,observed));test(!output_target::valid(observed,session,123));
 std::cout<<"Alpha target notice PASS "<<checks<<" checks;128 preallocated bytes;no asset bootstrap\n";
}
