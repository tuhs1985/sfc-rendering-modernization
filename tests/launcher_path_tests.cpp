#include "../tools/remix_runtime/launch_paths.h"
#include <fstream>
#include <iostream>
int wmain(int argc,wchar_t** argv){
 if(argc!=2)return 2;namespace fs=std::filesystem;unsigned checks=0;
 auto test=[&](bool good){++checks;if(!good)throw std::runtime_error("launcher paths check");};
 auto reject=[&](auto fn){try{fn();}catch(const std::exception&){test(true);return;}test(false);};
 try{
  const auto game=fs::absolute(argv[1])/L"Game \u65e5\u672c\u8a9e space",root=game/L"SFCRemix";
  const auto client=game/L"StarFleetOP.exe",launcher=root/L"runtime/remix-runtime/return-bin/return_launcher.exe";
  const auto immutable=launcher.parent_path()/L"SFCRemixReturn.dll",component=root/L"data/runs/test-in-game/SFCRemixReturn.dll",foreign=game.parent_path()/L"StarFleetOP.exe";
  for(auto path:{client,launcher,immutable,component,foreign}){fs::create_directories(path.parent_path());std::ofstream f(path);f<<"synthetic";}
  auto validate=[&](const fs::path& c,const fs::path& dll,const fs::path& exe,const fs::path& r){launch_paths::validate(c,dll,exe,r,false);};
  validate(client,component,launcher,root);test(true);validate(client,immutable,launcher,root);test(true);
  reject([&]{validate(foreign,component,launcher,root);});
  reject([&]{validate(client,component,client,root);});
  reject([&]{validate(client,foreign,launcher,root);});
  reject([&]{validate(client,component,launcher,{});});
  test(launch_paths::preload_name(component,game)=="SFCRemix\\data\\runs\\test-in-game\\SFCRemixReturn.dll");
  test(launch_paths::preload_name(immutable,game)=="SFCRemix\\runtime\\remix-runtime\\return-bin\\SFCRemixReturn.dll");
  reject([&]{launch_paths::preload_name(component,game.parent_path());});
  test(launch_paths::wait_limit(false,false,false,true)==INFINITE);
  test(launch_paths::wait_limit(false,false,true,true)==INFINITE);
  test(launch_paths::wait_limit(true,false,false,true)==60000);
  test(launch_paths::wait_limit(true,true,false,true)==100000);
  test(launch_paths::wait_limit(false,false,false,false)==300000);
  std::cout<<"Launcher paths PASS checks="<<checks<<" unicode_relative_import=1 no_game_process=1\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
