#include "../tools/m1_component/m1_identity_census.h"
#include "../tools/m1_component/m1_contract.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <limits>
int main(int argc,char** argv){
    unsigned checks=0;auto test=[&](bool okay){++checks;if(!okay){std::cerr<<"Identity census FAIL "<<checks<<'\n';std::exit(1);}};
    sfc_m1::OwnerTable<4> owners;
    const auto a=owners.observe(10,100,1),b=owners.observe(20,100,1),other=owners.observe(30,200,1);
    test(owners.model_owner(100,10,a.id)==a.id&&owners.model_owner(100,20,b.id)==b.id);
    test(owners.model_owner(100,0,0)==0&&owners.model_owner(200,0,0)==other.id);
    test(owners.model_owner(100,20,a.id)==0&&owners.model_owner(200,20,b.id)==0);
    owners.destroy_ship(20);const auto replacement=owners.observe(20,100,2);
    test(replacement.id!=b.id&&owners.model_owner(100,20,b.id)==0&&owners.model_owner(100,20,replacement.id)==replacement.id);
    sfc_m1::IdentityCensus census;using C=sfc_m1::IdentityCensus;C::Key key{};key[C::Kind]=1;key[C::Ship]=1;
    test(sizeof(census)<32768&&!census.enabled);census.record(key,1,0);
    census.record(key,555,9265);test(census.count==1&&census.observations==2&&census.entries[0].last_ms==9265);
    key[C::Visual]=2;census.record(key,556,9281);test(census.count==2&&census.entries[0].first_ms==0);
    for(unsigned i=2;i<C::Capacity;++i){key[C::Ship]=i+1;census.record(key,600+i,10000+i);}
    test(census.count==256&&census.omitted==0);key[C::Ship]=999;census.record(key,1000,20000);
    test(census.count==256&&census.omitted==1);
    key=census.entries[0].key;census.record(key,1001,20016);test(census.entries[0].observations==3&&census.omitted==1);
    std::ostringstream out;census.write(out);test(out.str().size()<C::OutputCap);
    // Worst-case numbers bound output even under arbitrary native pointer bits.
    for(auto& e:census.entries){e.key.fill(0xffffffffu);e.first_frame=e.last_frame=e.first_ms=e.last_ms=0xffffffffu;e.observations=std::numeric_limits<std::uint64_t>::max();}
    std::ostringstream maximum;census.write(maximum);test(maximum.str().size()<C::OutputCap);
    if(argc==2){std::ofstream f(argv[1]);f<<out.str();test(bool(f));}
    std::cout<<"Identity census PASS "<<checks<<" checks storage="<<sizeof(census)<<" output_cap="<<C::OutputCap<<'\n';
}
