// Actual startup consumer without a graphics device or SFC.
#include <windows.h>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <algorithm>
static void require(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
namespace fs=std::filesystem;
#include "../tools/m1_component/m1_present_calibration.h"
#include "../tools/d3d9_proof/warm_start.h"
int wmain(){try{warm_start::wait(fs::path(),[]{},[](const char*,unsigned){});std::cout<<"ACCEPTED\n";return 0;}
 catch(const warm_start::Cancelled&){std::cout<<"CANCELLED\n";return 10;}
 catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 20;}}
