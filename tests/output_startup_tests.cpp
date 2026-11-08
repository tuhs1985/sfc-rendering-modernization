#include "../tools/d3d9_proof/output_startup.h"
#include <iostream>
#include <stdexcept>
int main(){unsigned checks=0;auto test=[&](bool v){++checks;if(!v)throw std::runtime_error("output startup invariant");};
 output_startup::Control c{};c.parent=123;c.session=456;output_startup::seal(c);test(output_startup::valid(c,123,456));test(!output_startup::valid(c,124,456));test(!output_startup::valid(c,123,457));
 c.flags=2;output_startup::seal(c);test(!output_startup::valid(c,123,456));c.flags=1;output_startup::seal(c);test(output_startup::valid(c,123,456));
 c.asset[0]=1;test(!output_startup::valid(c,123,456));output_startup::seal(c);test(output_startup::valid(c,123,456));
 output_wire::Channel channel{};output_startup::write(channel,c);auto d=output_startup::read(channel);test(!memcmp(&c,&d,sizeof(c)));test(sizeof(channel)==192);test(sizeof(d)==128);
 output_startup::Lifetime clock(1000);test(!clock.expired(62000));test(!clock.activated);test(clock.activate(62000,60000));test(!clock.expired(121999));test(clock.expired(122000));test(!clock.activate(63000,60000));
 output_startup::Lifetime late(1000);test(late.expired(286000));test(!late.activate(286000,60000));
 output_startup::Lifetime play(1000,true);test(!play.expired(86400000));test(play.activate(86400000,0));
 test(!play.expired(172800000));test(!play.activate(172800000,60000));test(play.active==0);
 std::cout<<"Output startup PASS "<<checks<<" checks bits="<<sizeof(void*)*8<<'\n';}
