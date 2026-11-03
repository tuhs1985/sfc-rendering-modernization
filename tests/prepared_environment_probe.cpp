// Actual shared-memory bootstrap and light ownership;mock API,never GPU/SFC.
#define wmain unused_sfc_host_main
#include "../tools/d3d9_proof/d3d9_direct_host.cpp"
#undef wmain
static unsigned made=0,retired=0,waited=0;
static remixapi_ErrorCode REMIXAPI_CALL makeLight(const remixapi_LightInfo* info,remixapi_LightHandle* out){
 if(info->hash!=0x5346434e0002ull||!info->pNext)return REMIXAPI_ERROR_CODE_INVALID_ARGUMENTS;
 ++made;*out=reinterpret_cast<remixapi_LightHandle>(uintptr_t(123));return REMIXAPI_ERROR_CODE_SUCCESS;
}
static remixapi_ErrorCode REMIXAPI_CALL retireLight(remixapi_LightHandle){++retired;return REMIXAPI_ERROR_CODE_SUCCESS;}
int wmain(int argc,wchar_t** argv){
 if(argc!=3)return 2;SetEnvironmentVariableW(L"SFC_REMIX_CALIBRATION_SCENE",argv[1]);SetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",std::to_wstring(GetCurrentProcessId()).c_str());
 SetEnvironmentVariableW(L"SFC_D3D9_PREWARM",L"1");SetEnvironmentVariableW(L"SFC_D3D9_PREPARED_ENVIRONMENT",L"1");
 std::cin.get();std::string result="accepted";remixapi_Interface api{};api.CreateLight=makeLight;api.DestroyLight=retireLight;
 try{
  prepared_environment::Resource resource;
  resource.start(api,[&]{++waited;if(!wcscmp(argv[2],L"cancel-wait"))InterlockedExchange(&resource.ticket->state,startup_ticket::Cancelled);});
  if(!wcscmp(argv[2],L"transfer")){RemixLiveLights target;resource.transfer(target);resource.transfer(target);require(target.preparedHandle!=nullptr,"transferred actual resource");target.close(api);}
 }catch(const warm_start::Cancelled&){result="cancelled";}catch(const std::exception&){result="rejected";}
 std::cout<<"ENVIRONMENT_PROBE result="<<result<<" creates="<<made<<" destroys="<<retired<<" waits="<<waited<<'\n';return 0;
}
