// Remix-only type overrides, fixed808B v2 companion. Native packet stays200B.
#pragma once
#include <filesystem>
struct LightShapeRow{uint32_t slot,kind,ship,reserved;float v[28];char texture[128];};
struct LightShapePacket{uint32_t h[4];uint64_t revision,reserved;LightShapeRow rows[3];uint64_t checksum;};
static_assert(sizeof(LightShapeRow)==256&&sizeof(LightShapePacket)==808);
inline uint64_t shapeChecksum(const LightShapePacket& p){
 const auto* b=reinterpret_cast<const unsigned char*>(&p);uint64_t h=14695981039346656037ull;
 for(unsigned i=0;i<sizeof(p)-8;++i)h=(h^b[i])*1099511628211ull;return h;
}
inline bool validShapes(const LightShapePacket& p,uint64_t revision){
 if(p.h[0]!=0x50414853||p.h[1]!=2||p.h[2]!=sizeof(p)||p.h[3]!=3||p.revision!=revision||p.reserved||p.checksum!=shapeChecksum(p))return false;
 for(unsigned i=0;i<3;++i){const auto& r=p.rows[i];
  if(r.slot!=i||r.kind>6||r.ship>1||r.reserved>(i==2?1u:0u))return false;
  for(float f:r.v)if(!std::isfinite(f))return false;
  for(unsigned j=0;j<4;++j)if(r.v[j]<=0||r.v[j]>1e5f)return false;
  if(r.v[4]<0||r.v[4]>180||r.v[5]<0||r.v[5]>1||r.v[6]<0||r.v[6]>1000||std::abs(r.v[7])>360||std::abs(r.v[14])>360)return false;
  for(unsigned j=8;j<11;++j)if(std::abs(r.v[j])>1e6)return false;
  const float n=r.v[11]*r.v[11]+r.v[12]*r.v[12]+r.v[13]*r.v[13];if(std::abs(n-1)>.001f)return false;
  if(i==2){
   for(unsigned j=15;j<18;++j)if(r.v[j]<0||r.v[j]>1e6f)return false;
   const float dn=r.v[18]*r.v[18]+r.v[19]*r.v[19]+r.v[20]*r.v[20];if(std::abs(dn-1)>.001f)return false;
   if(r.v[21]<0||r.v[21]>180||r.v[22]<0||r.v[22]>16)return false;
  }
  for(unsigned j=i==2?23u:15u;j<28;++j)if(r.v[j])return false;
  if(r.kind==1){
   for(unsigned j=0;j<64;++j)if(!((r.texture[j]>='a'&&r.texture[j]<='f')||(r.texture[j]>='0'&&r.texture[j]<='9')))return false;
   if(memcmp(r.texture+64,".dds",4))return false;
   for(unsigned j=68;j<128;++j)if(r.texture[j])return false;
  }else for(char c:r.texture)if(c)return false;
 }return true;
}
inline remixapi_Float3D crossLight(remixapi_Float3D a,remixapi_Float3D b){return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
inline void lightBasis(remixapi_Float3D d,float roll,remixapi_Float3D& x,remixapi_Float3D& y){
 const auto ref=std::abs(d.y)<.9f?remixapi_Float3D{0,1,0}:remixapi_Float3D{1,0,0};
 x=crossLight(ref,d);const float n=std::sqrt(x.x*x.x+x.y*x.y+x.z*x.z);x={x.x/n,x.y/n,x.z/n};y=crossLight(d,x);
 const float angle=roll*.01745329252f,c=std::cos(angle),s=std::sin(angle);const auto a=x,b=y;
 x={c*a.x+s*b.x,c*a.y+s*b.y,c*a.z+s*b.z};y={-s*a.x+c*b.x,-s*a.y+c*b.y,-s*a.z+c*b.z};
}
inline remixapi_LightHandle createShapedLight(remixapi_Interface& api,const LiveLightRow& r,const LightShapeRow& shape){
 remixapi_LightInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;info.hash=0x5346434E0000ull+r.slot;
 info.radiance={r.values[3],r.values[4],r.values[5]};
 const auto& v=shape.v;const remixapi_Float3D direction{r.values[0],r.values[1],r.values[2]},position{v[8],v[9],v[10]};
 remixapi_LightInfoDistantEXT distant{};remixapi_LightInfoDomeEXT dome{};remixapi_LightInfoSphereEXT sphere{};
 remixapi_LightInfoRectEXT rect{};remixapi_LightInfoDiskEXT disk{};remixapi_LightInfoCylinderEXT cylinder{};
 std::wstring texture;
 switch(shape.kind){
 case 0:distant.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_DISTANT_EXT;distant.direction=direction;distant.angularDiameterDegrees=r.values[6];distant.volumetricRadianceScale=r.values[7];info.pNext=&distant;break;
 case 1:{dome.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_DOME_EXT;
  const float a=v[14]*.01745329252f;dome.transform.matrix[0][0]=std::cos(a);dome.transform.matrix[0][2]=std::sin(a);
  dome.transform.matrix[1][1]=1;dome.transform.matrix[2][0]=-std::sin(a);dome.transform.matrix[2][2]=std::cos(a);
  for(unsigned i=0;i<68;++i)texture+=static_cast<wchar_t>(shape.texture[i]);
  const auto path=std::filesystem::current_path()/L"textures"/texture;
  if(!std::filesystem::is_regular_file(path)||std::filesystem::file_size(path)>128*1024*1024)throw std::runtime_error("Dome DDS missing/bound");
  texture=path.wstring();dome.colorTexture=texture.c_str();info.pNext=&dome;break;}
 case 2:case 6:sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.position=position;sphere.radius=v[0];sphere.volumetricRadianceScale=r.values[7];
  if(shape.kind==6){sphere.shaping_hasvalue=TRUE;sphere.shaping_value={direction,v[4],v[5],v[6]};}info.pNext=&sphere;break;
 case 3:rect.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_RECT_EXT;rect.position=position;rect.direction=direction;lightBasis(direction,v[7],rect.xAxis,rect.yAxis);rect.xSize=v[1];rect.ySize=v[2];rect.volumetricRadianceScale=r.values[7];info.pNext=&rect;break;
 case 4:disk.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_DISK_EXT;disk.position=position;disk.direction=direction;lightBasis(direction,v[7],disk.xAxis,disk.yAxis);disk.xRadius=v[1]*.5f;disk.yRadius=v[2]*.5f;disk.volumetricRadianceScale=r.values[7];info.pNext=&disk;break;
 case 5:cylinder.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_CYLINDER_EXT;cylinder.position=position;cylinder.radius=v[0];cylinder.axis={v[11],v[12],v[13]};cylinder.axisLength=v[3];cylinder.volumetricRadianceScale=r.values[7];info.pNext=&cylinder;break;
 default:throw std::runtime_error("Unsupported light shape");
 }
 remixapi_LightHandle handle=nullptr;check(api.CreateLight(&info,&handle),"configured Remix light type");return handle;
}
