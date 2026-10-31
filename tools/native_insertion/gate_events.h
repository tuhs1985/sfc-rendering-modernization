#pragma once
#include "gate_contract.h"
#include <sddl.h>
#include <string>
namespace native_gate {
inline std::wstring eventName(const DWORD* session,const wchar_t* kind){wchar_t suffix[40]{};
 swprintf_s(suffix,L"%08x%08x%08x%08x",session[0],session[1],session[2],session[3]);return std::wstring(L"Local\\SFCNativeGate-")+kind+L"-"+suffix;}
struct Events {
 HANDLE ready=nullptr,stop=nullptr;
 Events()=default;Events(const Events&)=delete;Events& operator=(const Events&)=delete;
 ~Events(){if(ready)CloseHandle(ready);if(stop)CloseHandle(stop);}
 void open(const DWORD* session){
  ready=OpenEventW(SYNCHRONIZE|EVENT_MODIFY_STATE,FALSE,eventName(session,L"Ready").c_str());
  stop=OpenEventW(SYNCHRONIZE|EVENT_MODIFY_STATE,FALSE,eventName(session,L"Stop").c_str());
  if(!ready||!stop)throw std::runtime_error("Native gate events unavailable");
 }
 void create(const DWORD* session){
  HANDLE token=nullptr;if(!OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token))throw std::runtime_error("Gate token");
  alignas(TOKEN_USER) BYTE user[1024]{};DWORD bytes{};const BOOL got=GetTokenInformation(token,TokenUser,user,sizeof(user),&bytes);CloseHandle(token);
  if(!got)throw std::runtime_error("Gate token user");LPWSTR sid=nullptr;
  if(!ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(user)->User.Sid,&sid))throw std::runtime_error("Gate user SID");
  const std::wstring acl=std::wstring(L"D:P(A;;GA;;;")+sid+L")";LocalFree(sid);PSECURITY_DESCRIPTOR sd=nullptr;
  if(!ConvertStringSecurityDescriptorToSecurityDescriptorW(acl.c_str(),SDDL_REVISION_1,&sd,nullptr))throw std::runtime_error("Gate ACL");
  SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES),sd,FALSE};
  ready=CreateEventW(&security,FALSE,FALSE,eventName(session,L"Ready").c_str());
  stop=CreateEventW(&security,TRUE,FALSE,eventName(session,L"Stop").c_str());LocalFree(sd);
  if(!ready||!stop)throw std::runtime_error("Gate event creation");
 }
};
}
