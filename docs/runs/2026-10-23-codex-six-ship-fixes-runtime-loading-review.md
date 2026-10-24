# Run124 — six-ship correctness demonstrated;loading/reload latency remains

2026-10-23 America/New_York. Sponsor completed actual194205-307246-in-game:
everything loaded,almost30seconds for all ships,CLIappearedserial,eachload caused
wholeRemixscene flicker butNOToriginalgame. Read-only review of raw captures,
census,result,frame/input timing,material events,worker andcontroller logs.
HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,indexempty;priorworkpreserved.
FuelGuardattached;no source/config/budget change,game launch,helper or agent.

## Correctness — CONFIRMED

Six native ship/epoch pairs,sixpersistentowners,sixACKed catalogentries,sixdraw
counters. Five unique resident assets andonecontentalias. KDDowner1,FDD2,FCA3,
FFF4,KFF5and6. KFF6sharespath5/signaturewithKFF5butretainsownposition/instance.
Census26tuples/123952observations/zeroomitted,0–119985ms;no context-choice
mismatches andzero ownerretirements (previousmissingKDDchurnfixed).
FCAadmitted/drawn4455times;no assetpartial/rejections. Allmodels together image
accounting217153856bytes>old128MiBcap,168originalimages. NativeCPU/managedGPU
backing105951816bytes<256MiB. No need to increase any safetybound for thisfixture.

Drawcounts:KDD5072,FDD4909,FFF4705,FCA4455,KFF5=4182,KFF6=3908.
Zero cohort lookup,decode,projection or inputadmission failures. Persistent40156
publications/32957offscreenupdates,zero failed updates. Supported six-ship
correctness demonstrated;NOTall-model/large-mission/replacement or maturityPASS.

## Three distinct latency mechanisms

1. CONFIRMED sequentialworker admission,oneCPU preparation future,andGPUcreation
   onowningthread. Fiveuniqueassetloads,onealiaseswithoutnewbackendresource.
   Backendread/hashstage1.905–30.105ms;GPUadmission0.002–4.473ms. These numbers
   EXCLUDE Pythonimage/materialpreparation,scheduling andRemixreload;do not cite
   them as entireasset-loadcost. Material publicationsafterfirst:+5.469,+10.469,
   +15.954,+22.079seconds. This provides useful elapsed pipeline evidence,not a
   breakdown of all work insideeach Pythonstage.
2. CONFIRMEDfour longoutputGPUwaits alongsidefourlate material-libraryupdates:
   sourceframes470/804/1121/1512,1570.492/1291.929/1523.674/1116.483ms respectively.
   Total5.503secondsin thesefourwaits. Allreturnedshipsuseonecoherentimage;while
   outputislate,originalSFCcontinuesandourmatching-returnpolicyomitsunreadyimage.
   Sponsor'swholeRemixscene flickercorrelateswiththis. PriorRun117controlledA/B
   alreadyisolatedlatematerial-listrewrite. Exactvendorwatchdogstackstillinference,
   not a newprofilerconfirmation. Aliasentry6causesNOnewmateriallayerpublication.
3. CONFIRMEDlasttwo shipnative observationsarelate,not immediatecapturebacklog:
   capturedKDD0ms,FDD47ms,FFF63ms,FCA78ms,KFF5=20672ms,KFF6=29906ms.
   Censusfirstnativeowner5=20672ms,owner6=29906ms;this is when currentrenderseam
   firstobservedthem,NOTproofSFCdidnotalreadyknowtheirassetsormotion. Thusallships
   cannotappearbefore29.9secondsusingONLYtheseobservations. Do not attributeall
   of sponsor's30seconds toconversion or assertcameraactionsnotexplicitlyreported.

selected.preparation_seconds26.125startswithrelaysupervisorbeforemenus/gate;
NOT26seconds of modelconversion. Finalassetacktimeisnotrecordedwithstandalone
per-ownerwallclockprecision;drawcountsconfirmadmission,nottheexactlastappearance.
Additional end-to-end preparer stage spans are needed before selecting a parallel
worker count;simplyaddingthreads cannotremoveglobalmaterial reloadstalls.

After sourceframe2000,maxoutputGPUwait15.366ms,zero>50mswaits in retainedCSV.
Overallpaired5044/5411records,365withoutship,onewarmup/onereset;notliteralzero
flickerPASS. Knownstartup/reloaddeficiencyremains,notreclassifiedasacceptable.

## Cleanup,bounds and status

Finalerrornull,final_report_completetrue,normalexit,hooksrestored/unloaded,
rendererexit0,proxy/config/launchercriticalhashesrestoredPASS. Actualworkflow
159.86seconds<285,componentgateobservation120seconds,formalrecording90seconds.
Ownedjobexit0/stopreason0/noownedprocesses,peakscratch200560573bytes. Nativeevent
log619005bytes,nottruncated;runfolder218875173bytes. Allrawinputs/resultsignored.
Sponsor specificallyreportsoriginalgame unaffected;do not inventseparateHUD/
cursor/targetingacceptancebeyondthatstatement. No stage/commit/push.

## Recommended next bounded work (not implemented here)

Address scene-population throughput andnon-disruptivematerialregistration,not
another ownership-discoverytest or appearance tweak. Instrument the Python
preparer end-to-end,capture-to-ready andmaterialpublication intervals;reuse
alreadypreparedcontent. Determine a supported way to keep the material catalogue
stable while adding instances,or prepareknownmaterials before runtime rendering
begins. Do not patch vendorRemix,dropmaterialpolicy orholdwrongframepixels to
hideglobalreloadpauses. Earlierassetdiscoveryatloading/creation remains narrowly
unqualified and requiresseparateboundedinvestigation;lastowner's29.9sfirstoffer
isdirect evidencewhyitmatters. Geometry/texture sharing and six-ship ownership
are now proven underthisfixture;do notredo those proofsfromscratch.

Onlythisrecord,curatedevidenceandHANDOFFmodified;gitdiff--checkPASS,indexempty,
HEADunchanged,allpriorandnewworkunstaged/uncommitted. Exactnextaction:withsponsor
authorization,profileandremove serialpreparation/globalmaterialreloadbottlenecks
usingexistingcapturedsix-shipfixturebeforeanothergameplayrun.
