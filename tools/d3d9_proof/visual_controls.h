// Remix backend adapter only. Frozen worker-prepared baseline;no game callback IO.
#pragma once
static void check(HRESULT h,const char* why){ok(h,why);}
static void check(remixapi_ErrorCode e,const char* why){apiok(e,why);}
#include "../remix_runtime/remix_image_controls.h"
#include "../remix_runtime/remix_quality_controls.h"
#include "../remix_runtime/remix_image_adjust.h"
#include <thread>
#include <mutex>
#include <atomic>
struct DirectVisualControls {
 bool enabled=false;RemixImageControls image;RemixQualityControls quality;RemixImageAdjust grade;
 bool tuning=false;std::atomic<bool> stopping{false};std::thread reader;std::mutex mutex;
 RemixImageControls pendingImage;RemixQualityControls pendingQuality;unsigned messages=0;
 ~DirectVisualControls(){stopping=true;if(reader.joinable())reader.join();}
 void start(remixapi_Interface& api,ID3D11Device* device,ID3D11Texture2D* color){
  wchar_t flag[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_VISUAL_SETTINGS",flag,2)==1&&flag[0]==L'1';
  if(!enabled)return;
  require(image.read()&&quality.read(),"Prepared image/quality baseline required");
  auto set=[&](const char* key,const char* value){return api.SetConfigVariable(key,value)==REMIXAPI_ERROR_CODE_SUCCESS;};
  require(image.apply(set)&&quality.apply(set),"Pinned runtime rejected visual baseline");
  grade.prepare(device,color);
  std::cout<<"D3D9_VISUAL_BASELINE_APPLIED image="<<image.revision<<" quality="<<quality.revision<<"\n";
  tuning=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TUNING",flag,2)==1&&flag[0]==L'1';
  if(tuning){pendingImage=image;pendingQuality=quality;reader=std::thread([this,nextImage=image,nextQuality=quality]() mutable {
   while(!stopping){const bool changedImage=nextImage.read(),changedQuality=nextQuality.read();
    if(changedImage||changedQuality){std::lock_guard<std::mutex> lock(mutex);pendingImage=nextImage;pendingQuality=nextQuality;}
    Sleep(250);
   }
  });}
 }
 void poll(remixapi_Interface& api){
  if(!tuning)return;RemixImageControls nextImage;RemixQualityControls nextQuality;
  {std::unique_lock<std::mutex> lock(mutex,std::try_to_lock);if(!lock.owns_lock())return;nextImage=pendingImage;nextQuality=pendingQuality;}
  if(nextImage.revision==image.revision&&nextQuality.revision==quality.revision)return;
  auto set=[&](const char* key,const char* value){return api.SetConfigVariable(key,value)==REMIXAPI_ERROR_CODE_SUCCESS;};
  if(nextImage.apply(set)&&nextQuality.apply(set)){image=nextImage;quality=nextQuality;if(messages++<100)std::cout<<"D3D9_VISUAL_TUNING_APPLIED image="<<image.revision<<" quality="<<quality.revision<<"\n";}
  else {require(image.apply(set)&&quality.apply(set),"Live visual rollback failed");std::lock_guard<std::mutex> lock(mutex);pendingImage=image;pendingQuality=quality;if(messages++<100)std::cout<<"D3D9_VISUAL_TUNING_REJECTED last_good=1\n";}
 }
 bool apply(ID3D11DeviceContext* context,ID3D11Texture2D* color){
  // Queue grade and coverage together;caller fences the whole batch once.
  return enabled&&grade.draw(context,color,image.post());
 }
};
