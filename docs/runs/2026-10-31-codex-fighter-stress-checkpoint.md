# Run238 — fighter-heavy sponsor run; preliminary wrap-up

Sponsor reported a stress run with many fighters while requesting wrap-up at4% allowance. Read the completed summary only;full timing/visibility analysis is deferred. Run `20261031-212549-867833-in-game`.

- Final report complete,error null,normal game exit,controlled hook unload,controller/renderer exit0,no controller left running,proxy restored;accepted client and launcher settings unchanged.
-26fresh captures/transfers and26tracked owner identities across the session. Renderer loaded7unique assets and reused content19times;no rejected assets or unfinished preparation jobs. Catalog includes KDD,KCV,FCV,FFT,KFT,KCA,KCL. These are session totals,not a measured peak simultaneous count or visible model count;the sponsor's1–4-model fighter display observation remains unqualified.
- Native gate:5,025requests,37,579owner insertions,zero deadline misses/stale/invalid/partial/dropped gate records. Suppression receipts total92,124;these count native submission events and are not asserted to be one-to-one with insertion operations. Detailed source/list correlation remains available for later review.
-5,412frame records:median16.691ms,p9517.833ms,p9918.717ms,max30.895ms. This does not establish there were no perceptible hitches; sponsor visual feedback has not yet been collected.
- Persistent registry:26admitted,15destroyed,zero rejected;118,137pose publications,110,941offscreen,zero failed functional updates. Three diagnostic calibration misses did not block publication.
- Capture worker:26attempts,zero capture failures/owner overflow/invalid/IO failures/unsent assets.18coalesced/nonwaiting publication drops are distinct from gate record loss,which was zero. Renderer omitted342owner draws during eligibility/readiness;do not equate this aggregate with342visible whole-scene dropouts without detailed analysis. Retained renderer bytes49,143,288.

Changes remain unstaged/uncommitted;latest committed checkpoint is7320eae. No game/test launched during this wrap-up. Next after resume:review this run's detailed admission/visibility/timing evidence and sponsor observations before choosing another increment. SFC-22fighter display multiplicity stays deferred until most alpha work is complete. No100-object gameplay or alpha-completion claim.
