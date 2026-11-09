#pragma once
#include <windows.h>
#include <filesystem>
#include <stdexcept>
#include <string>
namespace launch_paths {
namespace fs=std::filesystem;
constexpr DWORD wait_limit(bool fixture,bool idleExperiment,bool lightTuning,bool play){
 return fixture?(idleExperiment?100000u:60000u):play?INFINITE:lightTuning?1980000u:300000u;
}
inline bool same(const fs::path& a,const fs::path& b){const auto x=a.lexically_normal().make_preferred(),y=b.lexically_normal().make_preferred();return CompareStringOrdinal(x.c_str(),-1,y.c_str(),-1,TRUE)==CSTR_EQUAL;}
inline void validate(const fs::path& client,const fs::path& component,const fs::path& launcher,const fs::path& releaseRoot,bool fixture){
 const auto c=fs::canonical(client),dll=fs::canonical(component);
 if(fixture){if(c.filename()!=L"d3d11_return_fixture.exe"||c.native().find(L"\\artifacts\\remix-runtime\\runs\\")==std::wstring::npos)throw std::runtime_error("not an owned fixture");return;}
 if(releaseRoot.empty()){
  if(!same(c,fs::path(L"C:\\Project\\SFC-Remix-Return-Test\\StarFleetOP.exe")))throw std::runtime_error("not the approved copied client");return;
 }
 const auto root=fs::canonical(releaseRoot);
 if(!same(root.filename(),L"SFCRemix")||!same(fs::canonical(launcher),root/L"runtime/remix-runtime/return-bin/return_launcher.exe")||
    !same(c,root.parent_path()/L"StarFleetOP.exe"))throw std::runtime_error("launcher/package/game path mismatch");
 const auto immutable=root/L"runtime/remix-runtime/return-bin/SFCRemixReturn.dll";
 const auto folder=dll.parent_path().filename().wstring();
 const bool runCopy=same(dll.parent_path().parent_path(),root/L"data/runs")&&folder.size()>8&&folder.substr(folder.size()-8)==L"-in-game"&&same(dll.filename(),L"SFCRemixReturn.dll");
 if(!same(dll,immutable)&&!runCopy)throw std::runtime_error("component outside package or owned run");
}
inline bool is_ascii(const std::wstring& value){for(auto c:value)if(c>127)return false;return true;}
inline std::string preload_name(const fs::path& component,const fs::path& directory){
 auto value=component.wstring();
 if(!is_ascii(value)){
  // Detours' import name is narrow even for CreateProcessW. Keep its suffix
  // ASCII and resolve it against the child's explicitly supplied Unicode CWD.
  const auto relative=fs::relative(component,directory);
  for(const auto& part:relative)if(part==L"..")throw std::runtime_error("Unicode preload must remain inside game copy");
  value=relative.wstring();
 }
 if(!is_ascii(value)||value.empty())throw std::runtime_error("preload import name is not ASCII");
 std::string result;result.reserve(value.size());for(auto c:value)result.push_back(static_cast<char>(c));return result;
}
}
