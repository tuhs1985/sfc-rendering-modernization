// LiveScene member definitions, included inside the class. Source qualification
// includes this .h alongside the existing native component inputs.
void breakBorn(DWORD child,DWORD parent,DWORD visual,DWORD piece){
    if(!breakEnabled||!enabled||!persistent||!cohort.store||!child||!parent||(parent&0x80000000u)||
       breaks.serial>=0x7fffffffu){++breakRejected;return;}
    for(auto& e:breaks.entries)if(e.live&&e.pointer==child){
        retire(0x80000000u|static_cast<DWORD>(e.epoch),persistentFrame,0);
        breaks.retire(child,e.epoch);break;
    }
    DWORD slot=0;for(;slot<owner_count;++slot)if(owners[slot].retired)break;
    if(slot==owner_count&&owner_count==kSceneOwners){++owner_overflow;return;}
    const auto epoch=breaks.born(child,parent,visual,piece);
    if(!epoch){++breakRejected;return;}
    if(slot==owner_count)++owner_count;
    const auto seq=owners[slot].sequence;owners[slot]={};auto& o=owners[slot];
    o.sequence=seq;o.breakPiece=true;o.breakEpoch=epoch;
    o.identity.owner=0x80000000u|static_cast<DWORD>(epoch);
    o.identity.ship=child;o.identity.visual=visual;++breakBornCount;
}
void breakRetire(DWORD child,DWORD frame,DWORD elapsed){
    for(auto& e:breaks.entries)if(e.live&&e.pointer==child){
        const auto epoch=e.epoch;retire(0x80000000u|static_cast<DWORD>(epoch),frame,elapsed);
        breaks.retire(child,epoch);++breakRetiredCount;return;
    }
}
template<class Read>SceneOwner* breakSubmission(DWORD child,std::uint64_t epoch,DWORD manager,
                                              DWORD& count,DWORD& primary,DWORD& secondary,Read read){
    for(DWORD slot=0;slot<owner_count;++slot){auto& o=owners[slot];
        if(!o.breakPiece||o.retired||o.failed||!o.revision||o.breakEpoch!=epoch||
           o.identity.ship!=child||o.identity.manager!=manager||!breakValid(o,read))continue;
        sfc_break::Layout l{};sfc_break::Range part{};
        const auto* e=breaks.find(child,epoch);DWORD second=0;
        if(!e||!sfc_break::layout(e->visual,l,read)||!sfc_break::range(l,e->piece,part)||
           l.model!=o.identity.model||l.source!=o.identity.source||part.list!=o.identity.list||part.count!=o.identity.count||
           !read(l.model+0x18,&second,4)||(second&&second>UINT32_MAX-part.first*4))return nullptr;
        count=part.count;primary=part.list;secondary=second?second+part.first*4:0;return &o;
    }
    return nullptr;
}
template<class Read>bool breakValid(const SceneOwner& o,Read read){
    DWORD vt=0,visual=0,piece=0,active=0;
    const auto* e=breaks.find(o.identity.ship,o.breakEpoch);
    return e&&!o.retired&&read(o.identity.ship,&vt,4)&&vt==0x007972b4&&
        read(o.identity.ship+0x9c,&visual,4)&&visual==e->visual&&
        read(o.identity.ship+0xa0,&piece,4)&&piece==e->piece&&
        read(o.identity.ship+0x24,&active,4)&&(active&255);
}
template<class Read>void observeBreak(DWORD child,DWORD manager,DWORD count,DWORD list,
                                     DWORD frame,DWORD elapsed,Read read){
    if(!breakEnabled||!enabled||!persistent||!cohort.store)return;
    for(DWORD slot=0;slot<owner_count;++slot){auto& o=owners[slot];
        if(!o.breakPiece||o.retired||o.identity.ship!=child)continue;
        const auto valid=[&](){return breakValid(o,read);};
        auto* e=breaks.find(child,o.breakEpoch);if(!e||!valid())return;
        sfc_break::Layout layout{};sfc_break::Range part{};
        if(!sfc_break::layout(e->visual,layout,read)||!sfc_break::range(layout,e->piece,part)||
           count!=part.count||list!=part.list){++breakRejected;return;}
        if(o.revision&&(o.identity.model!=layout.model||o.identity.source!=layout.source||
                       o.identity.count!=count||o.identity.list!=list)){
            ++breakRejected;retire(o.identity.owner,frame,elapsed);return;
        }
        auto& id=o.identity;id.model=layout.model;id.source=layout.source;id.manager=manager;
        id.thread=GetCurrentThreadId();id.frame=frame;id.elapsed=elapsed;id.caller=0x0042ea92;
        id.count=count;id.list=list;o.lod={1,0,0};
#ifdef SFC_NATIVE_LIGHT_DISCOVERY
        lights.observe(id,read,valid);
#endif
        if(o.revision||o.failed||last_capture_frame==frame)return;
        if(revisions==kSceneRevisions){o.failed=true;++capture_failures;return;}
        for(auto& a:assets)if(!InterlockedCompareExchange(&a.ready,0,0)){
            last_capture_frame=frame;++capture_attempts;
            const auto status=sfc_break::capture(a.mesh,layout,e->piece,id.owner,child,manager,read,valid);
            if(status!=MeshStatus::Complete){o.failed=true;++capture_failures;return;}
            a.mesh.header[MeshThread]=id.thread;a.mesh.header[MeshFrame]=frame;a.mesh.header[MeshElapsed]=elapsed;
            a.mesh.header[MeshHash]=a.mesh.checksum();capture_texture_references(a.refs,a.mesh,read,valid);
            if(a.refs.status!=1){o.failed=true;++capture_failures;return;}
            a.piece={id.owner,e->parent,e->piece,layout.pieceCount,part.first,part.count,layout.polygonCount,layout.polygons};
            if(!a.piece.valid()){o.failed=true;++capture_failures;return;}
            a.revision=++revisions;o.revision=a.revision;
            if(!breaks.asset(child,o.breakEpoch,e->visual,e->piece,o.revision)){o.failed=true;++capture_failures;return;}
            MemoryBarrier();InterlockedExchange(&a.ready,1);return;
        }
        return; // Busy transfer storage postpones capture; native drawing continues.
    }
}
template<class Read>void appendBreakRows(const std::array<DWORD,40>& camera,DWORD frame,DWORD elapsed,
                                        Read read,live_owner::Packet& anchor,bool& anchorPrepared){
    if(!breakEnabled)return;
    DWORD a=0,b=0,c=0;
    if(!read(0x00c69ff0,&a,4)||!read(0x00c69ff4,&b,4)||!read(0x00c74058,&c,4)||a||b||c){++breakRejected;return;}
    for(DWORD slot=0;slot<owner_count;++slot){auto& o=owners[slot];
        if(!o.breakPiece||o.retired||!o.revision||o.failed||!breakValid(o,read))continue;
        sfc_break::Pose world{};
        if(!sfc_break::simulation_pose(o.identity.ship,world,read)||
           !breaks.pose(o.identity.ship,o.breakEpoch,frame,world)){++persistentFailures;continue;}
        std::array<DWORD,96> r{};r[1]=o.identity.owner;r[2]=frame;r[3]=elapsed;r[4]=1;
        r[5]=o.identity.model;r[6]=o.identity.source;r[7]=o.revision;
        memcpy(r.data()+8,world.data(),64);r[24]=0x100;memcpy(r.data()+49,camera.data(),160);
        sfc_scene::Matrix v{},p{};memcpy(v.data(),camera.data(),64);memcpy(p.data(),camera.data()+17,64);
        auto viewport=sfc_scene::identity();float values[6]{};memcpy(values,camera.data()+34,24);
        viewport[0]=values[4];viewport[5]=-values[5];viewport[3]=values[0]+values[4];viewport[7]=values[1]+values[5];
        const auto composed=sfc_scene::multiply(viewport,sfc_scene::multiply(p,sfc_scene::multiply(v,world)));
        memcpy(r.data()+25,composed.data(),64);r[47]=GetCurrentThreadId();r[48]=1;
        LARGE_INTEGER q{};if(!QueryPerformanceCounter(&q))continue;sfc_calibration::stamp(r,q.QuadPart);
        if(directSource.prepare(r,anchor))anchorPrepared=true;
        if(slot<sfc_calibration::Owners&&!sfc_calibration::offer(calibration,slot,r))++calibrationMisses;
        cohort.offer(r); // Debris has no qualified intact-ship damage layer.
        if(!o.sequence||elapsed-o.last_ms>=34){o.last_ms=elapsed;offer(slot,r);}
        ++persistentPublications;
    }
}
