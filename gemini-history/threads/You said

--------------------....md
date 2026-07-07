[2026-07-04 22:16] User:
-------------------------------------

Translated Report (Full Report Below)

-------------------------------------




Process:               Google Chrome Canary [53209]

Path:                  /Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary

Identifier:            com.google.Chrome.canary

Version:               152.0.7931.0 (7931.0)

Code Type:             ARM-64 (Native)

Parent Process:        launchd [1]

User ID:               501




Date/Time:             2026-07-04 22:16:23.7928 -0600

OS Version:            macOS 15.7.8 (24G812)

Report Version:        12

Anonymous UUID:        93585FFB-0B9D-596C-DC3C-94E48637D423




Sleep/Wake UUID:       0FC7DD19-FE67-4103-87B7-F33D119CA77A




Time Awake Since Boot: 190000 seconds

Time Since Wake:       11345 seconds




System Integrity Protection: enabled




Crashed Thread:        12  ThreadPoolBackgroundWorker




Exception Type:        EXC_BAD_ACCESS (SIGBUS)

Exception Codes:       KERN_PROTECTION_FAILURE at 0x000000013cb102b4

Exception Codes:       0x0000000000000002, 0x000000013cb102b4




Termination Reason:    Namespace SIGNAL, Code 10 Bus error: 10

Terminating Process:   exc handler [53209]




VM Region Info: 0x13cb102b4 is in 0x13cb0c000-0x13cf0c000;  bytes after start: 17076  bytes before end: 4177227

      REGION TYPE                    START - END         [ VSIZE] PRT/MAX SHRMOD  REGION DETAIL

      VM_ALLOCATE                 13c90c000-13cb0c000    [ 2048K] rw-/rw- SM=PRV  

--->  mapped file                 13cb0c000-13cf0c000    [ 4096K] r--/r-- SM=PRV  Object_id=68a3850a

      mapped file                 13cf0c000-13cff4000    [  928K] r--/rw- SM=PRV  Object_id=e3d16d8




Thread 0:: CrBrowserMain Dispatch queue: com.apple.main-thread

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   HIToolbox                             0x19774327c RunCurrentEventLoopInMode + 324

8   HIToolbox                             0x1977464e8 ReceiveNextEventCommon + 676

9   HIToolbox                             0x1978d1484 _BlockUntilNextEventMatchingListInModeWithFilter + 76

10  AppKit                               0x18fbbea34 _DPSNextEvent + 684

11  AppKit                               0x19055d5cc -[NSApplication(NSEventRouting) _nextEventMatchingEventMask:untilDate:inMode:dequeue:] + 688

12  Google Chrome Framework               0x130790ba8 ChromeMain + 66633372

13  Google Chrome Framework               0x12caa3b90 ChromeMain + 2748036

14  Google Chrome Framework               0x130151f7c ChromeMain + 60084848

15  AppKit                               0x18fbb1be4 -[NSApplication run] + 480

16  Google Chrome Framework               0x12efaf91c ChromeMain + 41593872

17  Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

18  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

19  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

20  Google Chrome Framework               0x12f528cb8 ChromeMain + 47333292

21  Google Chrome Framework               0x12f52893c ChromeMain + 47332400

22  Google Chrome Framework               0x12e96e65c ChromeMain + 35035472

23  Google Chrome Framework               0x12e170ea4 ChromeMain + 26657176

24  Google Chrome Framework               0x12c804f28 ChromeMain + 540

25  Google Chrome Canary                 0x100e8c85c main + 196

26  dyld                                 0x18b812b98 start + 6076




Thread 1:: StackSamplingProfiler

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f5d54 ChromeMain + 9375816

5   Google Chrome Framework               0x12cad1f44 ChromeMain + 2937400

6   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

7   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

8   Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

9   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

10  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

11  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

12  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 2:

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12f627df8 ChromeMain + 48378092

5   Google Chrome Framework               0x12f627a84 ChromeMain + 48377208

6   Google Chrome Framework               0x138052b74 ChromeMain + 193257064

7   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

8   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 3:: HangWatcher

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f5d54 ChromeMain + 9375816

5   Google Chrome Framework               0x1345de050 ChromeMain + 131961668

6   Google Chrome Framework               0x1345de120 ChromeMain + 131961876

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 4:: PerfettoTrace

0   libsystem_kernel.dylib               0x18bb7d95c kevent64 + 8

1   Google Chrome Framework               0x12d507e50 ChromeMain + 13644100

2   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

3   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

4   Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

5   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

6   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

7   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

8   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 5:: ThreadPoolServiceThread

0   libsystem_kernel.dylib               0x18bb7d95c kevent64 + 8

1   Google Chrome Framework               0x12d507e50 ChromeMain + 13644100

2   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

3   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

4   Google Chrome Framework               0x1300cbdbc ChromeMain + 59535536

5   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

6   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

7   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

8   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 6:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 7:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 8:: ThreadPoolPresentationWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 9:: ThreadPoolAudioWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 10:: ThreadPoolBackgroundWorker

0   Google Chrome Framework               0x12f7f5abc ChromeMain + 50269616

1   Google Chrome Framework               0x1345f2b44 ChromeMain + 132046392

2   Google Chrome Framework               0x1345ea288 ChromeMain + 132011388

3   Google Chrome Framework               0x1331fc718 ChromeMain + 111114764

4   Google Chrome Framework               0x12d1ece64 ChromeMain + 10387800

5   Google Chrome Framework               0x12d0f82f0 ChromeMain + 9385444

6   Google Chrome Framework               0x12d0f777c ChromeMain + 9382512

7   Google Chrome Framework               0x12d0f49d0 ChromeMain + 9370820

8   Google Chrome Framework               0x12e07f468 ChromeMain + 25667420

9   Google Chrome Framework               0x12e07f2d8 ChromeMain + 25667020

10  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

11  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

12  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 11:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 12 Crashed:: ThreadPoolBackgroundWorker

0   Google Chrome Framework               0x12d8903d0 ChromeMain + 17348292

1   Google Chrome Framework               0x12d7531c8 ChromeMain + 16049340

2   Google Chrome Framework               0x12d751824 ChromeMain + 16042776

3   Google Chrome Framework               0x131671cf8 ChromeMain + 82235372

4   Google Chrome Framework               0x131672094 ChromeMain + 82236296

5   Google Chrome Framework               0x12dba6be8 ChromeMain + 20586204

6   Google Chrome Framework               0x1300ca9dc ChromeMain + 59530448

7   Google Chrome Framework               0x12d1ece64 ChromeMain + 10387800

8   Google Chrome Framework               0x12d0f82f0 ChromeMain + 9385444

9   Google Chrome Framework               0x12d0f777c ChromeMain + 9382512

10  Google Chrome Framework               0x12d0f49d0 ChromeMain + 9370820

11  Google Chrome Framework               0x12e07f468 ChromeMain + 25667420

12  Google Chrome Framework               0x12e07f2d8 ChromeMain + 25667020

13  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

14  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

15  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 13:: Chrome_IOThread

0   libsystem_kernel.dylib               0x18bb7d95c kevent64 + 8

1   Google Chrome Framework               0x12d507e50 ChromeMain + 13644100

2   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

3   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

4   Google Chrome Framework               0x12fff3c88 ChromeMain + 58650492

5   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

6   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

7   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

8   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 14:: MemoryInfra

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f5d54 ChromeMain + 9375816

5   Google Chrome Framework               0x12cad1f44 ChromeMain + 2937400

6   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

7   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

8   Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

9   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

10  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

11  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

12  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 15:: NetworkConfigWatcher

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   Google Chrome Framework               0x12efaf8a8 ChromeMain + 41593756

9   Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

10  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

11  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

12  Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

13  Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

14  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

15  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

16  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 16:: CrShutdownDetector

0   libsystem_kernel.dylib               0x18bb727dc read + 8

1   Google Chrome Framework               0x1331fe1fc ChromeMain + 111121648

2   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

3   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

4   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 17:: ThreadPoolSingleThreadForegroundBlocking

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f4c0 ChromeMain + 25667508

6   Google Chrome Framework               0x12e07f300 ChromeMain + 25667060

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 18:: NetworkConfigWatcher

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   Google Chrome Framework               0x12efaf8a8 ChromeMain + 41593756

9   Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

10  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

11  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

12  Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

13  Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

14  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

15  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

16  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 19:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 20:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 21:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 22:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 23:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 24:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 25:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 26:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 27:: NetworkNotificationThreadMac

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   Google Chrome Framework               0x12efaf8a8 ChromeMain + 41593756

9   Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

10  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

11  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

12  Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

13  Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

14  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

15  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

16  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 28:: ThreadPoolSingleThreadForegroundBlocking

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f4c0 ChromeMain + 25667508

6   Google Chrome Framework               0x12e07f300 ChromeMain + 25667060

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 29:: CacheThread_BlockFile

0   libsystem_kernel.dylib               0x18bb7d95c kevent64 + 8

1   Google Chrome Framework               0x12d507e50 ChromeMain + 13644100

2   Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

3   Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

4   Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

5   Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

6   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

7   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

8   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 30:: CompositorTileWorker1

0   libsystem_kernel.dylib               0x18bb753cc __psynch_cvwait + 8

1   libsystem_pthread.dylib               0x18bbb409c _pthread_cond_wait + 984

2   Google Chrome Framework               0x12fafc60c ChromeMain + 53442816

3   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

4   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

5   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 31:: ThreadPoolSingleThreadSharedBackgroundBlocking

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f4f8 ChromeMain + 25667564

6   Google Chrome Framework               0x12e07f314 ChromeMain + 25667080

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 32:: NetworkConfigWatcher

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   Google Chrome Framework               0x12efaf8a8 ChromeMain + 41593756

9   Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

10  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

11  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

12  Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

13  Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

14  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

15  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

16  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 33:: ThreadPoolSingleThreadSharedForeground

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f494 ChromeMain + 25667464

6   Google Chrome Framework               0x12e07f2ec ChromeMain + 25667040

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 34:: NetworkConfigWatcher

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   Google Chrome Framework               0x12efaf8a8 ChromeMain + 41593756

9   Google Chrome Framework               0x12efaf76c ChromeMain + 41593440

10  Google Chrome Framework               0x12e5e2eac ChromeMain + 31318432

11  Google Chrome Framework               0x12e5e2798 ChromeMain + 31316620

12  Google Chrome Framework               0x12e7bb654 ChromeMain + 33253704

13  Google Chrome Framework               0x12e7bb3c0 ChromeMain + 33253044

14  Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

15  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

16  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 35:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 36:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 37:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 38:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 39:: ThreadPoolForegroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f350 ChromeMain + 25667140

6   Google Chrome Framework               0x12e07f2a0 ChromeMain + 25666964

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 40:: com.apple.NSEventThread

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   AppKit                               0x18fce278c _NSEventThread + 140

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 41:: ThreadPoolBackgroundWorker

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   Google Chrome Framework               0x12d0f4d34 ChromeMain + 9371688

5   Google Chrome Framework               0x12e07f468 ChromeMain + 25667420

6   Google Chrome Framework               0x12e07f2d8 ChromeMain + 25667020

7   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

8   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

9   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 42:: org.libusb.device-hotplug

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   CoreFoundation                       0x18bd16314 CFRunLoopRun + 64

8   Google Chrome Framework               0x12f2c2044 ChromeMain + 44815160

9   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

10  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 43:: UsbEventHandler

0   libsystem_kernel.dylib               0x18bb7a498 poll + 8

1   Google Chrome Framework               0x12f096318 ChromeMain + 42538508

2   Google Chrome Framework               0x12f095fbc ChromeMain + 42537648

3   Google Chrome Framework               0x12de15ec8 ChromeMain + 23138748

4   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

5   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 44:

0   libsystem_pthread.dylib               0x18bbaeb6c start_wqthread + 0




Thread 45:: AXSpeech

0   libsystem_kernel.dylib               0x18bb71c34 mach_msg2_trap + 8

1   libsystem_kernel.dylib               0x18bb84338 mach_msg2_internal + 76

2   libsystem_kernel.dylib               0x18bb7a764 mach_msg_overwrite + 484

3   libsystem_kernel.dylib               0x18bb71fa8 mach_msg + 24

4   CoreFoundation                       0x18bc9ea7c __CFRunLoopServiceMachPort + 160

5   CoreFoundation                       0x18bc9d398 __CFRunLoopRun + 1208

6   CoreFoundation                       0x18bc9c858 CFRunLoopRunSpecific + 572

7   Foundation                           0x18d26cc78 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212

8   TextToSpeech                         0x1c2adfde0 0x1c2ab0000 + 196064

9   Foundation                           0x18d266ba8 __NSThread__start__ + 732

10  libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

11  libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 46:

0   libsystem_pthread.dylib               0x18bbaeb6c start_wqthread + 0




Thread 47:

0   libsystem_pthread.dylib               0x18bbaeb6c start_wqthread + 0




Thread 48:: caulk.messenger.shared:17

0   libsystem_kernel.dylib               0x18bb71bb0 semaphore_wait_trap + 8

1   caulk                                 0x19722acc8 caulk::semaphore::timed_wait(double) + 224

2   caulk                                 0x19722ab70 caulk::concurrent::details::worker_thread::run() + 32

3   caulk                                 0x19722a844 void* caulk::thread_proxy<std::__1::tuple<caulk::thread::attributes, void (caulk::concurrent::details::worker_thread::*)(), std::__1::tuple<caulk::concurrent::details::worker_thread*>>>(void*) + 96

4   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

5   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 49:: caulk.messenger.shared:high

0   libsystem_kernel.dylib               0x18bb71bb0 semaphore_wait_trap + 8

1   caulk                                 0x19722acc8 caulk::semaphore::timed_wait(double) + 224

2   caulk                                 0x19722ab70 caulk::concurrent::details::worker_thread::run() + 32

3   caulk                                 0x19722a844 void* caulk::thread_proxy<std::__1::tuple<caulk::thread::attributes, void (caulk::concurrent::details::worker_thread::*)(), std::__1::tuple<caulk::concurrent::details::worker_thread*>>>(void*) + 96

4   libsystem_pthread.dylib               0x18bbb3bc8 _pthread_start + 136

5   libsystem_pthread.dylib               0x18bbaeb80 thread_start + 8




Thread 50:

0   libsystem_pthread.dylib               0x18bbaeb6c start_wqthread + 0







Thread 12 crashed with ARM Thread State (64-bit):

    x0: 0x000001241cfc3540   x1: 0x0000000000000000   x2: 0x0000000000000004   x3: 0x00000000000000ff

    x4: 0x000001241eae4764   x5: 0x000001241f4f6984   x6: 0x0000000085845dd1   x7: 0x0000000000000000

    x8: 0x000000013cb102b4   x9: 0x00000000ffffffff  x10: 0x00000000009c0000  x11: 0x0000000101095744

   x12: 0x00000000009b0000  x13: 0x00000001306ecfcc  x14: 0x00000001300bfc00  x15: 0x00000001300bfc00

   x16: 0x00000000000003b0  x17: 0x0000012000095a00  x18: 0x0000000000000000  x19: 0x000001241cfc3540

   x20: 0x000000013ab0f770  x21: 0x000001240e03cae0  x22: 0x0000000000000000  x23: 0x000000013cb104b0

   x24: 0x000001240e03cab0  x25: 0x000001241cfc34e0  x26: 0x000000013cb1029c  x27: 0x000001240e14d5c0

   x28: 0x000000013ab0f770   fp: 0x00000001749f64a0   lr: 0x000000012d7531c8

    sp: 0x00000001749f6460   pc: 0x000000012d8903d0 cpsr: 0x60001000

   far: 0x000000013cb102b4  esr: 0x9200004f (Data Abort) byte write Permission fault




Binary Images:

       0x100e8c000 -        0x100e8ffff com.google.Chrome.canary (152.0.7931.0) <4c4c4433-5555-3144-a13a-b9838ddb8a02> /Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary

       0x12c800000 -        0x139c93fff com.google.Chrome.framework (152.0.7931.0) <4c4c4467-5555-3144-a1d6-bf44dc1e0502> /Applications/Google Chrome Canary.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/152.0.7931.0/Google Chrome Framework

       0x1162c0000 -        0x1162cbfff libobjc-trampolines.dylib (*) <9a87f143-aa9d-3c46-b2e8-b3fb9215e33e> /usr/lib/libobjc-trampolines.dylib

       0x11e304000 -        0x11ea0bfff com.apple.AGXMetalG14X (329.2) <5eb5e90f-6e4e-36eb-85f2-6be293d406f0> /System/Library/Extensions/AGXMetalG14X.bundle/Contents/MacOS/AGXMetalG14X

       0x13af00000 -        0x13be07fff liboptimization_guide_internal.dylib (*) <4c4c4411-5555-3144-a152-8b9f5ecdd6f5> /Applications/Google Chrome Canary.app/Contents/Frameworks/Google Chrome Framework.framework/Versions/152.0.7931.0/Libraries/liboptimization_guide_internal.dylib

       0x13d41c000 -        0x13d43bfff com.apple.security.csparser (3.0) <01a876b4-b197-318b-a47d-1feede3dc073> /System/Library/Frameworks/Security.framework/Versions/A/PlugIns/csparser.bundle/Contents/MacOS/csparser

       0x18bb71000 -        0x18bbac5f3 libsystem_kernel.dylib (*) <6f3df31d-047d-3869-b2e7-567ff5c99b26> /usr/lib/system/libsystem_kernel.dylib

       0x18bc22000 -        0x18c160fff com.apple.CoreFoundation (6.9) <bdc82415-a029-3463-ac49-1a792208ce00> /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation

       0x197680000 -        0x197986fdf com.apple.HIToolbox (2.1.1) <7537dc6d-3280-335e-9259-ed5d308d29ec> /System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/HIToolbox

       0x18fb84000 -        0x19101475f com.apple.AppKit (6.9) <58bf3551-b86d-3f23-b53c-8b391c9c64e0> /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit

       0x18b80c000 -        0x18b8a757b dyld (*) <9450f89f-91f2-3a28-b1fd-834d74c36cf8> /usr/lib/dyld

               0x0 - 0xffffffffffffffff ??? (*) <00000000-0000-0000-0000-000000000000> ???

       0x18bbad000 -        0x18bbb9a77 libsystem_pthread.dylib (*) <2886f4f3-500b-36c8-a20c-c457eb754e3d> /usr/lib/system/libsystem_pthread.dylib

       0x18d213000 -        0x18dffc5bf com.apple.Foundation (6.9) <39be75ac-350f-3b8c-9c10-8b2b5321ce8e> /System/Library/Frameworks/Foundation.framework/Versions/C/Foundation

       0x1c2ab0000 -        0x1c2cdbbbf com.apple.texttospeech (1.0.0) <c2fa2454-f671-3216-a1d0-28ad40e4e549> /System/Library/PrivateFrameworks/TextToSpeech.framework/Versions/A/TextToSpeech

       0x197229000 -        0x197250ddf com.apple.audio.caulk (1.0) <fa67137d-9735-3dce-8716-ab20f8cd6e24> /System/Library/PrivateFrameworks/caulk.framework/Versions/A/caulk




External Modification Summary:

  Calls made by other processes targeting this process:

    task_for_pid: 0

    thread_create: 0

    thread_set_state: 0

  Calls made by this process:

    task_for_pid: 0

    thread_create: 0

    thread_set_state: 0

  Calls made by all processes on this machine:

    task_for_pid: 0

    thread_create: 0

    thread_set_state: 0







-----------

Full Report

-----------




{"app_name":"Google Chrome Canary","timestamp":"2026-07-04 22:16:26.00 -0600","app_version":"152.0.7931.0","slice_uuid":"4c4c4433-5555-3144-a13a-b9838ddb8a02","build_version":"7931.0","platform":1,"bundleID":"com.google.Chrome.canary","share_with_app_devs":1,"is_first_party":0,"bug_type":"309","os_version":"macOS 15.7.8 (24G812)","roots_installed":0,"name":"Google Chrome Canary","incident_id":"46D974BC-69FA-4B6D-9086-011A121B97D5"}

{

  "uptime" : 190000,

  "procRole" : "Foreground",

  "version" : 2,

  "userID" : 501,

  "deployVersion" : 210,

  "modelCode" : "Mac14,10",

  "coalitionID" : 71821,

  "osVersion" : {

    "train" : "macOS 15.7.8",

    "build" : "24G812",

    "releaseType" : "User"

  },

  "captureTime" : "2026-07-04 22:16:23.7928 -0600",

  "codeSigningMonitor" : 1,

  "incident" : "46D974BC-69FA-4B6D-9086-011A121B97D5",

  "pid" : 53209,

  "translated" : false,

  "cpuType" : "ARM-64",

  "roots_installed" : 0,

  "bug_type" : "309",

  "procLaunch" : "2026-07-04 22:15:23.1772 -0600",

  "procStartAbsTime" : 4751594267995,

  "procExitAbsTime" : 4753047173509,

  "procName" : "Google Chrome Canary",

  "procPath" : "\/Applications\/Google Chrome Canary.app\/Contents\/MacOS\/Google Chrome Canary",

  "bundleInfo" : {"CFBundleShortVersionString":"152.0.7931.0","CFBundleVersion":"7931.0","CFBundleIdentifier":"com.google.Chrome.canary"},

  "storeInfo" : {"deviceIdentifierForVendor":"876BFD84-395D-5144-BDE0-39EB6EB11168","thirdParty":true},

  "parentProc" : "launchd",

  "parentPid" : 1,

  "coalitionName" : "com.google.Chrome.canary",

  "crashReporterKey" : "93585FFB-0B9D-596C-DC3C-94E48637D423",

  "appleIntelligenceStatus" : {"state":"available"},

  "codeSigningID" : "com.google.Chrome.canary",

  "codeSigningTeamID" : "EQHXZ8M8AV",

  "codeSigningFlags" : 570522369,

  "codeSigningValidationCategory" : 6,

  "codeSigningTrustLevel" : 4294967295,

  "codeSigningAuxiliaryInfo" : 0,

  "instructionByteStream" : {"beforePC":"aBJA+T8ACOthCwBUYIIC2eCFBtAAYBaRnM69lWgKQPkIUQCRCQCAEg==","atPC":"CIEpuB8FADHoA4gaFX0QUzUCADQWPQASaBJA+R8BFuupAQBUdIJC2Q=="},

  "bootSessionUUID" : "503E0D5F-7212-4EBF-A930-A57C06A63ADF",

  "wakeTime" : 11345,

  "sleepWakeUUID" : "0FC7DD19-FE67-4103-87B7-F33D119CA77A",

  "sip" : "enabled",

  "vmRegionInfo" : "0x13cb102b4 is in 0x13cb0c000-0x13cf0c000;  bytes after start: 17076  bytes before end: 4177227\n      REGION TYPE                    START - END         [ VSIZE] PRT\/MAX SHRMOD  REGION DETAIL\n      VM_ALLOCATE                 13c90c000-13cb0c000    [ 2048K] rw-\/rw- SM=PRV  \n--->  mapped file                 13cb0c000-13cf0c000    [ 4096K] r--\/r-- SM=PRV  Object_id=68a3850a\n      mapped file                 13cf0c000-13cff4000    [  928K] r--\/rw- SM=PRV  Object_id=e3d16d8",

  "exception" : {"codes":"0x0000000000000002, 0x000000013cb102b4","rawCodes":[2,5313200820],"type":"EXC_BAD_ACCESS","signal":"SIGBUS","subtype":"KERN_PROTECTION_FAILURE at 0x000000013cb102b4"},

  "termination" : {"flags":0,"code":10,"namespace":"SIGNAL","indicator":"Bus error: 10","byProc":"exc handler","byPid":53209},

  "vmregioninfo" : "0x13cb102b4 is in 0x13cb0c000-0x13cf0c000;  bytes after start: 17076  bytes before end: 4177227\n      REGION TYPE                    START - END         [ VSIZE] PRT\/MAX SHRMOD  REGION DETAIL\n      VM_ALLOCATE                 13c90c000-13cb0c000    [ 2048K] rw-\/rw- SM=PRV  \n--->  mapped file                 13cb0c000-13cf0c000    [ 4096K] r--\/r-- SM=PRV  Object_id=68a3850a\n      mapped file                 13cf0c000-13cff4000    [  928K] r--\/rw- SM=PRV  Object_id=e3d16d8",

  "extMods" : {"caller":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"system":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"targeted":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"warnings":0},

  "faultingThread" : 12,

  "threads" : [{"threadState":{"x":[{"value":0},{"value":21592279046},{"value":8589934592},{"value":46192373268480},{"value":0},{"value":46192373268480},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":10755},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":46192373268480},{"value":0},{"value":46192373268480},{"value":6156650328},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6156650176},"sp":{"value":6156650096},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"id":15121217,"name":"CrBrowserMain","queue":"com.apple.main-thread","frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":799356,"symbol":"RunCurrentEventLoopInMode","symbolLocation":324,"imageIndex":8},{"imageOffset":812264,"symbol":"ReceiveNextEventCommon","symbolLocation":676,"imageIndex":8},{"imageOffset":2430084,"symbol":"_BlockUntilNextEventMatchingListInModeWithFilter","symbolLocation":76,"imageIndex":8},{"imageOffset":240180,"symbol":"_DPSNextEvent","symbolLocation":684,"imageIndex":9},{"imageOffset":10327500,"symbol":"-[NSApplication(NSEventRouting) _nextEventMatchingEventMask:untilDate:inMode:dequeue:]","symbolLocation":688,"imageIndex":9},{"imageOffset":66653096,"symbol":"ChromeMain","symbolLocation":66633372,"imageIndex":1},{"imageOffset":2767760,"symbol":"ChromeMain","symbolLocation":2748036,"imageIndex":1},{"imageOffset":60104572,"symbol":"ChromeMain","symbolLocation":60084848,"imageIndex":1},{"imageOffset":187364,"symbol":"-[NSApplication run]","symbolLocation":480,"imageIndex":9},{"imageOffset":41613596,"symbol":"ChromeMain","symbolLocation":41593872,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":47353016,"symbol":"ChromeMain","symbolLocation":47333292,"imageIndex":1},{"imageOffset":47352124,"symbol":"ChromeMain","symbolLocation":47332400,"imageIndex":1},{"imageOffset":35055196,"symbol":"ChromeMain","symbolLocation":35035472,"imageIndex":1},{"imageOffset":26676900,"symbol":"ChromeMain","symbolLocation":26657176,"imageIndex":1},{"imageOffset":20264,"symbol":"ChromeMain","symbolLocation":540,"imageIndex":1},{"imageOffset":2140,"symbol":"main","symbolLocation":196,"imageIndex":0},{"imageOffset":27544,"symbol":"start","symbolLocation":6076,"imageIndex":10}]},{"id":15121223,"name":"StackSamplingProfiler","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":65983582568448},{"value":0},{"value":65983582568448},{"value":32},{"value":60000},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":15363},{"value":4294945451},{"value":18446744073709551569},{"value":0},{"value":0},{"value":60000},{"value":32},{"value":65983582568448},{"value":0},{"value":65983582568448},{"value":6166785136},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6166784416},"sp":{"value":6166784336},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9395540,"symbol":"ChromeMain","symbolLocation":9375816,"imageIndex":1},{"imageOffset":2957124,"symbol":"ChromeMain","symbolLocation":2937400,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121232,"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":48397816,"symbol":"ChromeMain","symbolLocation":48378092,"imageIndex":1},{"imageOffset":48396932,"symbol":"ChromeMain","symbolLocation":48377208,"imageIndex":1},{"imageOffset":193276788,"symbol":"ChromeMain","symbolLocation":193257064,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}],"threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":0},{"value":0},{"value":47309064765440},{"value":48},{"value":0},{"value":0},{"value":17179869184},{"value":48},{"value":0},{"value":0},{"value":0},{"value":11015},{"value":0},{"value":18446744073709551569},{"value":8501548512},{"value":0},{"value":0},{"value":48},{"value":47309064765440},{"value":0},{"value":0},{"value":4311187456},{"value":0},{"value":17179870210},{"value":18446744073709550527},{"value":1026}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6158363344},"sp":{"value":6158363264},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}}},{"id":15121250,"name":"HangWatcher","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":181466663223296},{"value":0},{"value":181466663223296},{"value":32},{"value":10000},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":42251},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":18446744073709551569},{"value":1236951181824},{"value":0},{"value":10000},{"value":32},{"value":181466663223296},{"value":0},{"value":181466663223296},{"value":6175780448},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6175779728},"sp":{"value":6175779648},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9395540,"symbol":"ChromeMain","symbolLocation":9375816,"imageIndex":1},{"imageOffset":131981392,"symbol":"ChromeMain","symbolLocation":131961668,"imageIndex":1},{"imageOffset":131981600,"symbol":"ChromeMain","symbolLocation":131961876,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121251,"name":"PerfettoTrace","threadState":{"x":[{"value":4},{"value":0},{"value":0},{"value":1236972203792},{"value":1},{"value":0},{"value":0},{"value":0},{"value":0},{"value":30},{"value":30},{"value":1},{"value":1236950665560},{"value":1236950900736},{"value":4294705156},{"value":4294945451},{"value":369},{"value":1236951180288},{"value":0},{"value":1236953037064},{"value":1236970934560},{"value":1236953036800},{"value":1236972203792},{"value":1236952837128},{"value":41219},{"value":1236952838000},{"value":12297829382473034411},{"value":1236951181048},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5055217232},"cpsr":{"value":2684358656},"fp":{"value":6184201616},"sp":{"value":6184201296},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639049052},"far":{"value":0}},"frames":[{"imageOffset":51548,"symbol":"kevent64","symbolLocation":8,"imageIndex":6},{"imageOffset":13663824,"symbol":"ChromeMain","symbolLocation":13644100,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121252,"name":"ThreadPoolServiceThread","threadState":{"x":[{"value":1},{"value":0},{"value":0},{"value":1254131380000},{"value":6},{"value":0},{"value":0},{"value":0},{"value":0},{"value":588},{"value":588},{"value":198043264250},{"value":1236950665800},{"value":1236974780416},{"value":18446744073709551615},{"value":928320},{"value":369},{"value":0},{"value":0},{"value":1236953032456},{"value":1236970933792},{"value":1236953032192},{"value":1254131380000},{"value":1236952835080},{"value":34051},{"value":1236952835952},{"value":12297829382473034411},{"value":1236951184120},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5055217232},"cpsr":{"value":2147487744},"fp":{"value":6192622992},"sp":{"value":6192622672},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639049052},"far":{"value":0}},"frames":[{"imageOffset":51548,"symbol":"kevent64","symbolLocation":8,"imageIndex":6},{"imageOffset":13663824,"symbol":"ChromeMain","symbolLocation":13644100,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":59555260,"symbol":"ChromeMain","symbolLocation":59535536,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121253,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":174835233718272},{"value":0},{"value":174835233718272},{"value":32},{"value":1712},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":40707},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1236951184896},{"value":0},{"value":1712},{"value":32},{"value":174835233718272},{"value":0},{"value":174835233718272},{"value":6201044576},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6201043712},"sp":{"value":6201043632},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121254,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":173735722090496},{"value":0},{"value":173735722090496},{"value":32},{"value":1713},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":40451},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1236951189504},{"value":0},{"value":1713},{"value":32},{"value":173735722090496},{"value":0},{"value":173735722090496},{"value":6209465952},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6209465088},"sp":{"value":6209465008},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121255,"name":"ThreadPoolPresentationWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":149546466279424},{"value":0},{"value":149546466279424},{"value":32},{"value":60756},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":34819},{"value":256},{"value":18446744073709551569},{"value":1236951187968},{"value":0},{"value":60756},{"value":32},{"value":149546466279424},{"value":0},{"value":149546466279424},{"value":6217887328},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6217886464},"sp":{"value":6217886384},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121256,"name":"ThreadPoolAudioWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":172636210462720},{"value":0},{"value":172636210462720},{"value":32},{"value":60756},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":40195},{"value":0},{"value":18446744073709551569},{"value":8501548536},{"value":0},{"value":60756},{"value":32},{"value":172636210462720},{"value":0},{"value":172636210462720},{"value":6226308704},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6226307840},"sp":{"value":6226307760},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121257,"name":"ThreadPoolBackgroundWorker","threadState":{"x":[{"value":1236965660672},{"value":1254672196224},{"value":1145208553792},{"value":6234727616},{"value":359415680},{"value":32},{"value":7306087014534637922},{"value":0},{"value":1254601530296},{"value":1},{"value":29280},{"value":16384},{"value":64},{"value":16383},{"value":4294770691},{"value":4294945451},{"value":6639250416,"symbolLocation":0,"symbol":"pthread_getspecific"},{"value":8501548504},{"value":0},{"value":6234728080},{"value":1254601529216},{"value":1254601530296},{"value":3188326136196712625},{"value":648},{"value":163208757249},{"value":6234727808},{"value":6234727776},{"value":1254483033200},{"value":1236951192596}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5091842824},"cpsr":{"value":536875008},"fp":{"value":6234727728},"sp":{"value":6234727696},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":5091842748},"far":{"value":0}},"frames":[{"imageOffset":50289340,"symbol":"ChromeMain","symbolLocation":50269616,"imageIndex":1},{"imageOffset":132066116,"symbol":"ChromeMain","symbolLocation":132046392,"imageIndex":1},{"imageOffset":132031112,"symbol":"ChromeMain","symbolLocation":132011388,"imageIndex":1},{"imageOffset":111134488,"symbol":"ChromeMain","symbolLocation":111114764,"imageIndex":1},{"imageOffset":10407524,"symbol":"ChromeMain","symbolLocation":10387800,"imageIndex":1},{"imageOffset":9405168,"symbol":"ChromeMain","symbolLocation":9385444,"imageIndex":1},{"imageOffset":9402236,"symbol":"ChromeMain","symbolLocation":9382512,"imageIndex":1},{"imageOffset":9390544,"symbol":"ChromeMain","symbolLocation":9370820,"imageIndex":1},{"imageOffset":25687144,"symbol":"ChromeMain","symbolLocation":25667420,"imageIndex":1},{"imageOffset":25686744,"symbol":"ChromeMain","symbolLocation":25667020,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121258,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":170437187207168},{"value":0},{"value":170437187207168},{"value":32},{"value":1713},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":39683},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":18446744073709551569},{"value":1236951191040},{"value":0},{"value":1713},{"value":32},{"value":170437187207168},{"value":0},{"value":170437187207168},{"value":6243151456},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6243150592},"sp":{"value":6243150512},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"triggered":true,"id":15121259,"name":"ThreadPoolBackgroundWorker","threadState":{"x":[{"value":1254616741184},{"value":0},{"value":4},{"value":255},{"value":1254645188452},{"value":1254655748484},{"value":2240044497},{"value":0},{"value":5313200820},{"value":4294967295},{"value":10223616},{"value":4312356676},{"value":10158080},{"value":5107535820,"symbolLocation":65962688,"symbol":"ChromeMain"},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":944},{"value":1236951194112},{"value":0},{"value":1254616741184},{"value":5279643504},{"value":1254365580000},{"value":0},{"value":5313201328},{"value":1254365579952},{"value":1254616741088},{"value":5313200796},{"value":1254366696896},{"value":5279643504}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5057622472},"cpsr":{"value":1610616832},"fp":{"value":6251570336},"sp":{"value":6251570272},"esr":{"value":2449473615,"description":"(Data Abort) byte write Permission fault"},"pc":{"value":5058921424,"matchesCrashFrame":1},"far":{"value":5313200820}},"frames":[{"imageOffset":17368016,"symbol":"ChromeMain","symbolLocation":17348292,"imageIndex":1},{"imageOffset":16069064,"symbol":"ChromeMain","symbolLocation":16049340,"imageIndex":1},{"imageOffset":16062500,"symbol":"ChromeMain","symbolLocation":16042776,"imageIndex":1},{"imageOffset":82255096,"symbol":"ChromeMain","symbolLocation":82235372,"imageIndex":1},{"imageOffset":82256020,"symbol":"ChromeMain","symbolLocation":82236296,"imageIndex":1},{"imageOffset":20605928,"symbol":"ChromeMain","symbolLocation":20586204,"imageIndex":1},{"imageOffset":59550172,"symbol":"ChromeMain","symbolLocation":59530448,"imageIndex":1},{"imageOffset":10407524,"symbol":"ChromeMain","symbolLocation":10387800,"imageIndex":1},{"imageOffset":9405168,"symbol":"ChromeMain","symbolLocation":9385444,"imageIndex":1},{"imageOffset":9402236,"symbol":"ChromeMain","symbolLocation":9382512,"imageIndex":1},{"imageOffset":9390544,"symbol":"ChromeMain","symbolLocation":9370820,"imageIndex":1},{"imageOffset":25687144,"symbol":"ChromeMain","symbolLocation":25667420,"imageIndex":1},{"imageOffset":25686744,"symbol":"ChromeMain","symbolLocation":25667020,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121260,"name":"Chrome_IOThread","threadState":{"x":[{"value":1},{"value":0},{"value":0},{"value":1254390786048},{"value":75},{"value":0},{"value":0},{"value":2},{"value":0},{"value":100000},{"value":9223372036854775808},{"value":198043298250},{"value":1236951471616},{"value":16383},{"value":4294639621},{"value":4294945451},{"value":369},{"value":0},{"value":0},{"value":1236953035528},{"value":1236970930720},{"value":1236953035264},{"value":1236972195056},{"value":72057594037927935},{"value":233535},{"value":1236952826736},{"value":12297829382473034411},{"value":1236951196408},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5055217232},"cpsr":{"value":2147487744},"fp":{"value":6259993984},"sp":{"value":6259993664},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639049052},"far":{"value":0}},"frames":[{"imageOffset":51548,"symbol":"kevent64","symbolLocation":8,"imageIndex":6},{"imageOffset":13663824,"symbol":"ChromeMain","symbolLocation":13644100,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":58670216,"symbol":"ChromeMain","symbolLocation":58650492,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121261,"name":"MemoryInfra","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":192427419762688},{"value":0},{"value":192427419762688},{"value":32},{"value":2730},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":44803},{"value":4294945451},{"value":18446744073709551569},{"value":1236951197184},{"value":0},{"value":2730},{"value":32},{"value":192427419762688},{"value":0},{"value":192427419762688},{"value":6268415088},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6268414368},"sp":{"value":6268414288},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9395540,"symbol":"ChromeMain","symbolLocation":9375816,"imageIndex":1},{"imageOffset":2957124,"symbol":"ChromeMain","symbolLocation":2937400,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121262,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":272691768590336},{"value":0},{"value":272691768590336},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":63491},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":272691768590336},{"value":0},{"value":272691768590336},{"value":6276832680},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6276832528},"sp":{"value":6276832448},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":41613480,"symbol":"ChromeMain","symbolLocation":41593756,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121263,"name":"CrShutdownDetector","threadState":{"x":[{"value":4},{"value":0},{"value":4},{"value":6285258851},{"value":6285258168},{"value":18},{"value":0},{"value":0},{"value":18},{"value":8484456664,"symbolLocation":0,"symbol":"_current_pid"},{"value":8026668483491361347},{"value":3298534884098},{"value":160},{"value":16383},{"value":4294377481},{"value":4294945451},{"value":3},{"value":8501556912},{"value":0},{"value":1254130528688},{"value":0},{"value":6285258556},{"value":4},{"value":5279651800},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5152694780},"cpsr":{"value":1610616832},"fp":{"value":6285258608},"sp":{"value":6285258240},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639003612},"far":{"value":0}},"frames":[{"imageOffset":6108,"symbol":"read","symbolLocation":8,"imageIndex":6},{"imageOffset":111141372,"symbol":"ChromeMain","symbolLocation":111121648,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121264,"name":"ThreadPoolSingleThreadForegroundBlocking","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":199058849267712},{"value":0},{"value":199058849267712},{"value":32},{"value":60397},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":46347},{"value":1},{"value":18446744073709551569},{"value":5054532092,"symbolLocation":12958960,"symbol":"ChromeMain"},{"value":0},{"value":60397},{"value":32},{"value":199058849267712},{"value":0},{"value":199058849267712},{"value":6293679712},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6293678848},"sp":{"value":6293678768},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25687232,"symbol":"ChromeMain","symbolLocation":25667508,"imageIndex":1},{"imageOffset":25686784,"symbol":"ChromeMain","symbolLocation":25667060,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121265,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":202323024412672},{"value":0},{"value":202323024412672},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":47107},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":202323024412672},{"value":0},{"value":202323024412672},{"value":6302096808},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6302096656},"sp":{"value":6302096576},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":41613480,"symbol":"ChromeMain","symbolLocation":41593756,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121267,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":263895675568128},{"value":0},{"value":263895675568128},{"value":32},{"value":60873},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":61443},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":18446744073709551569},{"value":1254137077248},{"value":0},{"value":60873},{"value":32},{"value":263895675568128},{"value":0},{"value":263895675568128},{"value":6310522464},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6310521600},"sp":{"value":6310521520},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121268,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":205621559296000},{"value":0},{"value":205621559296000},{"value":32},{"value":60248},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":47875},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137083392},{"value":0},{"value":60248},{"value":32},{"value":205621559296000},{"value":0},{"value":205621559296000},{"value":6318943840},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6318942976},"sp":{"value":6318942896},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121269,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":206721070923776},{"value":0},{"value":206721070923776},{"value":32},{"value":60248},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":48131},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":18446744073709551569},{"value":1254137081856},{"value":0},{"value":60248},{"value":32},{"value":206721070923776},{"value":0},{"value":206721070923776},{"value":6327365216},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6327364352},"sp":{"value":6327364272},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121270,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":259497629057024},{"value":0},{"value":259497629057024},{"value":32},{"value":60247},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":60419},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137084928},{"value":0},{"value":60247},{"value":32},{"value":259497629057024},{"value":0},{"value":259497629057024},{"value":6335786592},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6335785728},"sp":{"value":6335785648},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121271,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":211119117434880},{"value":0},{"value":211119117434880},{"value":32},{"value":60829},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":49155},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137086464},{"value":0},{"value":60829},{"value":32},{"value":211119117434880},{"value":0},{"value":211119117434880},{"value":6344207968},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6344207104},"sp":{"value":6344207024},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121272,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":212218629062656},{"value":0},{"value":212218629062656},{"value":32},{"value":60236},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":49411},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137088000},{"value":0},{"value":60236},{"value":32},{"value":212218629062656},{"value":0},{"value":212218629062656},{"value":6352629344},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6352628480},"sp":{"value":6352628400},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121273,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":213318140690432},{"value":0},{"value":213318140690432},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":49667},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137089536},{"value":0},{"value":60235},{"value":32},{"value":213318140690432},{"value":0},{"value":213318140690432},{"value":6361050720},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6361049856},"sp":{"value":6361049776},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121274,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":257298605801472},{"value":0},{"value":257298605801472},{"value":32},{"value":60236},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":59907},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137091072},{"value":0},{"value":60236},{"value":32},{"value":257298605801472},{"value":0},{"value":257298605801472},{"value":6369472096},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6369471232},"sp":{"value":6369471152},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121275,"name":"NetworkNotificationThreadMac","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":248502512779264},{"value":0},{"value":248502512779264},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":57859},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":248502512779264},{"value":0},{"value":248502512779264},{"value":6377889192},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6377889040},"sp":{"value":6377888960},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":41613480,"symbol":"ChromeMain","symbolLocation":41593756,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121276,"name":"ThreadPoolSingleThreadForegroundBlocking","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":241905443012608},{"value":0},{"value":241905443012608},{"value":32},{"value":60346},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":56323},{"value":2863311531},{"value":18446744073709551569},{"value":1254137094144},{"value":0},{"value":60346},{"value":32},{"value":241905443012608},{"value":0},{"value":241905443012608},{"value":6386314848},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6386313984},"sp":{"value":6386313904},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25687232,"symbol":"ChromeMain","symbolLocation":25667508,"imageIndex":1},{"imageOffset":25686784,"symbol":"ChromeMain","symbolLocation":25667060,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121277,"name":"CacheThread_BlockFile","threadState":{"x":[{"value":1},{"value":0},{"value":0},{"value":1254139696272},{"value":2},{"value":0},{"value":0},{"value":0},{"value":0},{"value":17638},{"value":17638},{"value":198043266875},{"value":1254181310464},{"value":1254181310464},{"value":24},{"value":18},{"value":369},{"value":1254284654496},{"value":0},{"value":1254132111624},{"value":1254134518560},{"value":1254132111360},{"value":8000},{"value":1254131003400},{"value":1},{"value":1254131004272},{"value":12297829382473034411},{"value":1254137096440},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5055217232},"cpsr":{"value":2147487744},"fp":{"value":6394736016},"sp":{"value":6394735696},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639049052},"far":{"value":0}},"frames":[{"imageOffset":51548,"symbol":"kevent64","symbolLocation":8,"imageIndex":6},{"imageOffset":13663824,"symbol":"ChromeMain","symbolLocation":13644100,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121278,"name":"CompositorTileWorker1","threadState":{"x":[{"value":260},{"value":0},{"value":328960},{"value":0},{"value":0},{"value":161},{"value":0},{"value":0},{"value":6403157528},{"value":0},{"value":1024},{"value":4398046512130},{"value":4398046512130},{"value":1024},{"value":0},{"value":4398046512128},{"value":305},{"value":8501548296},{"value":0},{"value":1254132818584},{"value":1254132818712},{"value":6403158240},{"value":0},{"value":0},{"value":328960},{"value":328961},{"value":329216},{"value":0},{"value":5276409856}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639272092},"cpsr":{"value":1610616832},"fp":{"value":6403157648},"sp":{"value":6403157504},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639014860},"far":{"value":0}},"frames":[{"imageOffset":17356,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":6},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":12},{"imageOffset":53462540,"symbol":"ChromeMain","symbolLocation":53442816,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121360,"name":"ThreadPoolSingleThreadSharedBackgroundBlocking","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":355189500411904},{"value":0},{"value":355189500411904},{"value":32},{"value":60524},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":82699},{"value":2863311531},{"value":18446744073709551569},{"value":1254137111040},{"value":0},{"value":60524},{"value":32},{"value":355189500411904},{"value":0},{"value":355189500411904},{"value":6411578976},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6411578112},"sp":{"value":6411578032},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25687288,"symbol":"ChromeMain","symbolLocation":25667564,"imageIndex":1},{"imageOffset":25686804,"symbol":"ChromeMain","symbolLocation":25667080,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121362,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":344160024395776},{"value":0},{"value":344160024395776},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":80131},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":344160024395776},{"value":0},{"value":344160024395776},{"value":6419996072},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6419995920},"sp":{"value":6419995840},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":41613480,"symbol":"ChromeMain","symbolLocation":41593756,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121363,"name":"ThreadPoolSingleThreadSharedForeground","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":340861489512448},{"value":0},{"value":340861489512448},{"value":32},{"value":1713},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":79363},{"value":2863311531},{"value":18446744073709551569},{"value":1254137106432},{"value":0},{"value":1713},{"value":32},{"value":340861489512448},{"value":0},{"value":340861489512448},{"value":6428421728},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6428420864},"sp":{"value":6428420784},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25687188,"symbol":"ChromeMain","symbolLocation":25667464,"imageIndex":1},{"imageOffset":25686764,"symbol":"ChromeMain","symbolLocation":25667040,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121368,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":311174675562496},{"value":0},{"value":311174675562496},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":72451},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":311174675562496},{"value":0},{"value":311174675562496},{"value":6436838824},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6436838672},"sp":{"value":6436838592},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":41613480,"symbol":"ChromeMain","symbolLocation":41593756,"imageIndex":1},{"imageOffset":41613164,"symbol":"ChromeMain","symbolLocation":41593440,"imageIndex":1},{"imageOffset":31338156,"symbol":"ChromeMain","symbolLocation":31318432,"imageIndex":1},{"imageOffset":31336344,"symbol":"ChromeMain","symbolLocation":31316620,"imageIndex":1},{"imageOffset":33273428,"symbol":"ChromeMain","symbolLocation":33253704,"imageIndex":1},{"imageOffset":33272768,"symbol":"ChromeMain","symbolLocation":33253044,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121403,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":557465280184320},{"value":0},{"value":557465280184320},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":129795},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137120256},{"value":0},{"value":60235},{"value":32},{"value":557465280184320},{"value":0},{"value":557465280184320},{"value":12893302368},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12893301504},"sp":{"value":12893301424},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121404,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":378244884856832},{"value":0},{"value":378244884856832},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":88067},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137124864},{"value":0},{"value":60235},{"value":32},{"value":378244884856832},{"value":0},{"value":378244884856832},{"value":12910145120},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12910144256},"sp":{"value":12910144176},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121405,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":377248452444160},{"value":0},{"value":377248452444160},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":87835},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137123328},{"value":0},{"value":60235},{"value":32},{"value":377248452444160},{"value":0},{"value":377248452444160},{"value":12901723744},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12901722880},"sp":{"value":12901722800},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121406,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":380443908112384},{"value":0},{"value":380443908112384},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":88579},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137104896},{"value":0},{"value":60235},{"value":32},{"value":380443908112384},{"value":0},{"value":380443908112384},{"value":12918566496},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12918565632},"sp":{"value":12918565552},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121407,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":381543419740160},{"value":0},{"value":381543419740160},{"value":32},{"value":60235},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":88835},{"value":18446744073709551615},{"value":18446744073709551569},{"value":1254137126400},{"value":0},{"value":60235},{"value":32},{"value":381543419740160},{"value":0},{"value":381543419740160},{"value":12926987872},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12926987008},"sp":{"value":12926986928},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25686864,"symbol":"ChromeMain","symbolLocation":25667140,"imageIndex":1},{"imageOffset":25686688,"symbol":"ChromeMain","symbolLocation":25666964,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15121500,"name":"com.apple.NSEventThread","threadState":{"x":[{"value":0},{"value":21592279046},{"value":8589934592},{"value":746598460030976},{"value":0},{"value":746598460030976},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":173831},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":746598460030976},{"value":0},{"value":746598460030976},{"value":6437986440},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6437986288},"sp":{"value":6437986208},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":1435532,"symbol":"_NSEventThread","symbolLocation":140,"imageIndex":9},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15122111,"name":"ThreadPoolBackgroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869442},{"value":0},{"value":1045665622786048},{"value":0},{"value":1045665622786048},{"value":32},{"value":33000},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":243463},{"value":5101059072,"symbolLocation":59485940,"symbol":"ChromeMain"},{"value":18446744073709551569},{"value":1254271177728},{"value":0},{"value":33000},{"value":32},{"value":1045665622786048},{"value":0},{"value":1045665622786048},{"value":12935409248},{"value":0},{"value":17179870466},{"value":18446744073709550527},{"value":1282}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":12935408384},"sp":{"value":12935408304},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":9391412,"symbol":"ChromeMain","symbolLocation":9371688,"imageIndex":1},{"imageOffset":25687144,"symbol":"ChromeMain","symbolLocation":25667420,"imageIndex":1},{"imageOffset":25686744,"symbol":"ChromeMain","symbolLocation":25667020,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15122115,"name":"org.libusb.device-hotplug","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":1043449419661312},{"value":0},{"value":1043449419661312},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":242947},{"value":0},{"value":18446744073709551569},{"value":10236681961532652720,"symbolLocation":10236681953013137424,"symbol":"libSystem_initializer.libkernel_funcs"},{"value":0},{"value":4294967295},{"value":2},{"value":1043449419661312},{"value":0},{"value":1043449419661312},{"value":6438559784},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6438559632},"sp":{"value":6438559552},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":1000212,"symbol":"CFRunLoopRun","symbolLocation":64,"imageIndex":7},{"imageOffset":44834884,"symbol":"ChromeMain","symbolLocation":44815160,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15122116,"name":"UsbEventHandler","threadState":{"x":[{"value":4},{"value":0},{"value":60000},{"value":241923},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":60000},{"value":2},{"value":1},{"value":8484456792,"symbolLocation":0,"symbol":"vm_page_size"},{"value":0},{"value":4294945451},{"value":230},{"value":8501556912},{"value":0},{"value":1254270442240},{"value":1254302996160},{"value":2},{"value":60},{"value":5280317440},{"value":0},{"value":1254270442584},{"value":1254270442576},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":5084111640},"cpsr":{"value":1610616832},"fp":{"value":12943830480},"sp":{"value":12943830400},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639035544},"far":{"value":0}},"frames":[{"imageOffset":38040,"symbol":"poll","symbolLocation":8,"imageIndex":6},{"imageOffset":42558232,"symbol":"ChromeMain","symbolLocation":42538508,"imageIndex":1},{"imageOffset":42557372,"symbol":"ChromeMain","symbolLocation":42537648,"imageIndex":1},{"imageOffset":23158472,"symbol":"ChromeMain","symbolLocation":23138748,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15125517,"frames":[{"imageOffset":7020,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":12}],"threadState":{"x":[{"value":6167359488},{"value":204643},{"value":6166822912},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":4096},"fp":{"value":0},"sp":{"value":6167359488},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639250284},"far":{"value":0}}},{"id":15128850,"name":"AXSpeech","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":930491779776512},{"value":0},{"value":930491779776512},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":216647},{"value":0},{"value":18446744073709551569},{"value":8501550176},{"value":0},{"value":4294967295},{"value":2},{"value":930491779776512},{"value":0},{"value":930491779776512},{"value":6157213112},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6639076152},"cpsr":{"value":4096},"fp":{"value":6157212960},"sp":{"value":6157212880},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000628},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":78648,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":6},{"imageOffset":38756,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":6},{"imageOffset":4008,"symbol":"mach_msg","symbolLocation":24,"imageIndex":6},{"imageOffset":510588,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":7},{"imageOffset":504728,"symbol":"__CFRunLoopRun","symbolLocation":1208,"imageIndex":7},{"imageOffset":501848,"symbol":"CFRunLoopRunSpecific","symbolLocation":572,"imageIndex":7},{"imageOffset":367736,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":13},{"imageOffset":196064,"imageIndex":14},{"imageOffset":342952,"symbol":"__NSThread__start__","symbolLocation":732,"imageIndex":13},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15128857,"frames":[{"imageOffset":7020,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":12}],"threadState":{"x":[{"value":6439710720},{"value":243255},{"value":6439174144},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":4096},"fp":{"value":0},"sp":{"value":6439710720},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639250284},"far":{"value":0}}},{"id":15128859,"frames":[{"imageOffset":7020,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":12}],"threadState":{"x":[{"value":6440857600},{"value":111639},{"value":6440321024},{"value":6440856448},{"value":1982472},{"value":1},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":4096},"fp":{"value":0},"sp":{"value":6440856448},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639250284},"far":{"value":0}}},{"id":15128910,"name":"caulk.messenger.shared:17","threadState":{"x":[{"value":14},{"value":1254366202122},{"value":0},{"value":6441431146},{"value":1254366202096},{"value":25},{"value":0},{"value":0},{"value":0},{"value":4294967295},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":18446744073709551580},{"value":8501552624},{"value":0},{"value":1254550556608},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6830599368},"cpsr":{"value":2147487744},"fp":{"value":6441430912},"sp":{"value":6441430880},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000496},"far":{"value":0}},"frames":[{"imageOffset":2992,"symbol":"semaphore_wait_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":7368,"symbol":"caulk::semaphore::timed_wait(double)","symbolLocation":224,"imageIndex":15},{"imageOffset":7024,"symbol":"caulk::concurrent::details::worker_thread::run()","symbolLocation":32,"imageIndex":15},{"imageOffset":6212,"symbol":"void* caulk::thread_proxy<std::__1::tuple<caulk::thread::attributes, void (caulk::concurrent::details::worker_thread::*)(), std::__1::tuple<caulk::concurrent::details::worker_thread*>>>(void*)","symbolLocation":96,"imageIndex":15},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15128911,"name":"caulk.messenger.shared:high","threadState":{"x":[{"value":14},{"value":1254366229244},{"value":0},{"value":6442004588},{"value":1254366229216},{"value":27},{"value":0},{"value":0},{"value":0},{"value":4294967295},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":18446744073709551580},{"value":8501552624},{"value":0},{"value":1254494117632},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6830599368},"cpsr":{"value":2147487744},"fp":{"value":6442004352},"sp":{"value":6442004320},"esr":{"value":1442840704,"description":" Address size fault"},"pc":{"value":6639000496},"far":{"value":0}},"frames":[{"imageOffset":2992,"symbol":"semaphore_wait_trap","symbolLocation":8,"imageIndex":6},{"imageOffset":7368,"symbol":"caulk::semaphore::timed_wait(double)","symbolLocation":224,"imageIndex":15},{"imageOffset":7024,"symbol":"caulk::concurrent::details::worker_thread::run()","symbolLocation":32,"imageIndex":15},{"imageOffset":6212,"symbol":"void* caulk::thread_proxy<std::__1::tuple<caulk::thread::attributes, void (caulk::concurrent::details::worker_thread::*)(), std::__1::tuple<caulk::concurrent::details::worker_thread*>>>(void*)","symbolLocation":96,"imageIndex":15},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":12},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":12}]},{"id":15128920,"frames":[{"imageOffset":7020,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":12}],"threadState":{"x":[{"value":12944977920},{"value":0},{"value":12944441344},{"value":0},{"value":278532},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":4096},"fp":{"value":0},"sp":{"value":12944977920},"esr":{"value":0,"description":" Address size fault"},"pc":{"value":6639250284},"far":{"value":0}}}],

  "usedImages" : [

  {

    "source" : "P",

    "arch" : "arm64",

    "base" : 4310220800,

    "CFBundleShortVersionString" : "152.0.7931.0",

    "CFBundleIdentifier" : "com.google.Chrome.canary",

    "size" : 16384,

    "uuid" : "4c4c4433-5555-3144-a13a-b9838ddb8a02",

    "path" : "\/Applications\/Google Chrome Canary.app\/Contents\/MacOS\/Google Chrome Canary",

    "name" : "Google Chrome Canary",

    "CFBundleVersion" : "7931.0"

  },

  {

    "source" : "P",

    "arch" : "arm64",

    "base" : 5041553408,

    "CFBundleShortVersionString" : "152.0.7931.0",

    "CFBundleIdentifier" : "com.google.Chrome.framework",

    "size" : 222904320,

    "uuid" : "4c4c4467-5555-3144-a1d6-bf44dc1e0502",

    "path" : "\/Applications\/Google Chrome Canary.app\/Contents\/Frameworks\/Google Chrome Framework.framework\/Versions\/152.0.7931.0\/Google Chrome Framework",

    "name" : "Google Chrome Framework",

    "CFBundleVersion" : "7931.0"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 4666949632,

    "size" : 49152,

    "uuid" : "9a87f143-aa9d-3c46-b2e8-b3fb9215e33e",

    "path" : "\/usr\/lib\/libobjc-trampolines.dylib",

    "name" : "libobjc-trampolines.dylib"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 4801445888,

    "CFBundleShortVersionString" : "329.2",

    "CFBundleIdentifier" : "com.apple.AGXMetalG14X",

    "size" : 7372800,

    "uuid" : "5eb5e90f-6e4e-36eb-85f2-6be293d406f0",

    "path" : "\/System\/Library\/Extensions\/AGXMetalG14X.bundle\/Contents\/MacOS\/AGXMetalG14X",

    "name" : "AGXMetalG14X",

    "CFBundleVersion" : "329.2"

  },

  {

    "source" : "P",

    "arch" : "arm64",

    "base" : 5283774464,

    "size" : 15761408,

    "uuid" : "4c4c4411-5555-3144-a152-8b9f5ecdd6f5",

    "path" : "\/Applications\/Google Chrome Canary.app\/Contents\/Frameworks\/Google Chrome Framework.framework\/Versions\/152.0.7931.0\/Libraries\/liboptimization_guide_internal.dylib",

    "name" : "liboptimization_guide_internal.dylib"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 5322686464,

    "CFBundleShortVersionString" : "3.0",

    "CFBundleIdentifier" : "com.apple.security.csparser",

    "size" : 131072,

    "uuid" : "01a876b4-b197-318b-a47d-1feede3dc073",

    "path" : "\/System\/Library\/Frameworks\/Security.framework\/Versions\/A\/PlugIns\/csparser.bundle\/Contents\/MacOS\/csparser",

    "name" : "csparser",

    "CFBundleVersion" : "61439.140.12.706.1"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6638997504,

    "size" : 243188,

    "uuid" : "6f3df31d-047d-3869-b2e7-567ff5c99b26",

    "path" : "\/usr\/lib\/system\/libsystem_kernel.dylib",

    "name" : "libsystem_kernel.dylib"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6639722496,

    "CFBundleShortVersionString" : "6.9",

    "CFBundleIdentifier" : "com.apple.CoreFoundation",

    "size" : 5500928,

    "uuid" : "bdc82415-a029-3463-ac49-1a792208ce00",

    "path" : "\/System\/Library\/Frameworks\/CoreFoundation.framework\/Versions\/A\/CoreFoundation",

    "name" : "CoreFoundation",

    "CFBundleVersion" : "3603.1.411"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6835142656,

    "CFBundleShortVersionString" : "2.1.1",

    "CFBundleIdentifier" : "com.apple.HIToolbox",

    "size" : 3174368,

    "uuid" : "7537dc6d-3280-335e-9259-ed5d308d29ec",

    "path" : "\/System\/Library\/Frameworks\/Carbon.framework\/Versions\/A\/Frameworks\/HIToolbox.framework\/Versions\/A\/HIToolbox",

    "name" : "HIToolbox"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6706184192,

    "CFBundleShortVersionString" : "6.9",

    "CFBundleIdentifier" : "com.apple.AppKit",

    "size" : 21563232,

    "uuid" : "58bf3551-b86d-3f23-b53c-8b391c9c64e0",

    "path" : "\/System\/Library\/Frameworks\/AppKit.framework\/Versions\/C\/AppKit",

    "name" : "AppKit",

    "CFBundleVersion" : "2575.70.57"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6635438080,

    "size" : 636284,

    "uuid" : "9450f89f-91f2-3a28-b1fd-834d74c36cf8",

    "path" : "\/usr\/lib\/dyld",

    "name" : "dyld"

  },

  {

    "size" : 0,

    "source" : "A",

    "base" : 0,

    "uuid" : "00000000-0000-0000-0000-000000000000"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6639243264,

    "size" : 51832,

    "uuid" : "2886f4f3-500b-36c8-a20c-c457eb754e3d",

    "path" : "\/usr\/lib\/system\/libsystem_pthread.dylib",

    "name" : "libsystem_pthread.dylib"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6662729728,

    "CFBundleShortVersionString" : "6.9",

    "CFBundleIdentifier" : "com.apple.Foundation",

    "size" : 14587328,

    "uuid" : "39be75ac-350f-3b8c-9c10-8b2b5321ce8e",

    "path" : "\/System\/Library\/Frameworks\/Foundation.framework\/Versions\/C\/Foundation",

    "name" : "Foundation",

    "CFBundleVersion" : "3603.1.411"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 7560953856,

    "CFBundleShortVersionString" : "1.0.0",

    "CFBundleIdentifier" : "com.apple.texttospeech",

    "size" : 2276288,

    "uuid" : "c2fa2454-f671-3216-a1d0-28ad40e4e549",

    "path" : "\/System\/Library\/PrivateFrameworks\/TextToSpeech.framework\/Versions\/A\/TextToSpeech",

    "name" : "TextToSpeech",

    "CFBundleVersion" : "1.0"

  },

  {

    "source" : "P",

    "arch" : "arm64e",

    "base" : 6830592000,

    "CFBundleShortVersionString" : "1.0",

    "CFBundleIdentifier" : "com.apple.audio.caulk",

    "size" : 163296,

    "uuid" : "fa67137d-9735-3dce-8716-ab20f8cd6e24",

    "path" : "\/System\/Library\/PrivateFrameworks\/caulk.framework\/Versions\/A\/caulk",

    "name" : "caulk"

  }

],

  "sharedCache" : {

  "base" : 6634602496,

  "size" : 5039898624,

  "uuid" : "c74f10a4-5eb1-3813-b9fc-856e65c639e0"

},

  "legacyInfo" : {

  "threadTriggered" : {

    "name" : "ThreadPoolBackgroundWorker"

  }

},

  "logWritingSignature" : "b2a4fe855c75533f9652e06f678d64bf74d61c08",

  "trialInfo" : {

  "rollouts" : [

    {

      "rolloutId" : "60f8ddccefea4203d95cbeef",

      "factorPackIds" : {




      },

      "deploymentId" : 240000025

    },

    {

      "rolloutId" : "66d35d7fe4d6bf7664f40ddf",

      "factorPackIds" : {

        "BLACKPEARL_SPARROW" : "67c7824a1baae429bb41b897"

      },

      "deploymentId" : 240000067

    }

  ],

  "experiments" : [




  ]

}

}




Model: Mac14,10, BootROM mBoot-18000.160.14.0.1, proc 12:8:4 processors, 16 GB, SMC 

Graphics: Apple M2 Pro, Apple M2 Pro, Built-In

Display: Color LCD, 3456 x 2234 Retina, Main, MirrorOff, Online

Memory Module: LPDDR5, Micron

AirPort: spairport_wireless_card_type_wifi (0x14E4, 0x4388), wl0: Jun 24 2025 05:20:23 version 23.40.31.0.41.51.179 FWID 01-b816d667

IO80211_driverkit-1485.14 "IO80211_driverkit-1485.14" May 20 2026 22:23:19

AirPort: 

Bluetooth: Version (null), 0 services, 0 devices, 0 incoming serial ports

Network Service: Wi-Fi, AirPort, en0

USB Device: USB31Bus

USB Device: USB31Bus

USB Device: USB31Bus

Thunderbolt Bus: MacBook Pro, Apple Inc.

Thunderbolt Bus: MacBook Pro, Apple Inc.

Thunderbolt Bus: MacBook Pro, Apple Inc.

---

[2026-07-04 22:16] Assistant:
This crash is an **`EXC_BAD_ACCESS (SIGBUS)`** caused by a **`KERN_PROTECTION_FAILURE`** in Google Chrome Canary.

Here is the exact breakdown of why it happened and how to address it.

The Root Cause Analysis
1. The Crash Trigger

**Crashed Thread:** Thread 12 (`ThreadPoolBackgroundWorker`)

**Exception Type:** `EXC_BAD_ACCESS (SIGBUS)`

**Subtype:** `KERN_PROTECTION_FAILURE at 0x000000013cb102b4`

**ESR (Exception Syndrome Register):** `Data Abort, byte write Permission fault`

A background worker thread tried to execute a memory **write operation** to a specific address (`0x000000013cb102b4`).

2. The Memory Violation

Looking at the **VM Region Info**, we can see exactly what that address points to:

Plaintext

```
--->  mapped file        13cb0c000-13cf0c000    [ 4096K] r--/r-- SM=PRV

```


The target memory address lives inside a memory-mapped file region that is explicitly marked as **Read-Only (`r--/r--`)**.

Because the binary code attempted to write data into a block of memory intended only for reading, the macOS kernel blocked the operation and terminated Chrome immediately with a Bus Error 10 to ensure system security and stability.

Why Is This Happening?

Because this occurred on **Chrome Canary** (v152.0.7931.0), it is highly likely a **regression bug** introduced in a recent overnight build.

Background thread operations inside Chromium typically handle file caching, preference syncing, compilation optimization, or database management. A pointer tracking a memory-mapped resource likely lost its state or was incorrectly cast to a mutable type, telling the worker thread it was safe to write there when it wasn’t.

How to Fix It
1. The Immediate Workaround (Clear Caches)

Since the crash involves a `mapped file` region handled by a background worker, clearing out local corrupted cache files often resolves the loop.

Completely close Chrome Canary.

Open your terminal and remove the Canary cache directory:

Bash

```
rm -rf ~/Library/Caching/Google/Chrome\ Canary/

```


If it persists, you may need to clear out the default profile state file maps (make sure your profile sync is active so you don't lose open tabs permanently):

Bash

```
rm -rf ~/Library/Application\ Support/Google/Chrome\ Canary/Default/File\ System/

```

2. The Practical Solution

Because Canary updates daily, bugs like memory management faults are usually caught by automated telemetry within 24 to 48 hours.

Check for an updated build directly via `Chrome -> About Google Chrome Canary` if you can open it long enough, or download a fresh installer sheet from the official channel.

Switch back to standard Chrome Stable or Chrome Dev temporarily while the Chromium team resolves the permission mapping regression in this specific version sequence.
