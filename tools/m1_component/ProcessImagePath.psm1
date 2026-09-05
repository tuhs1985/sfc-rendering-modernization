function Get-M1ProcessImagePath {
    [CmdletBinding()]
    param([Parameter(Mandatory)][ValidateRange(1, 2147483647)][int]$ProcessId)

    # MainModule requires more access than querying the process image name.
    # Never substitute an installation path: it may not belong to this PID.
    if (-not ('SfcM1.ProcessImageQuery' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
namespace SfcM1 {
    public static class ProcessImageQuery {
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern bool QueryFullProcessImageNameW(
            IntPtr process, uint flags, StringBuilder path, ref uint size);
        [DllImport("kernel32.dll")]
        private static extern bool CloseHandle(IntPtr handle);
        public static string Read(int pid) {
            // PROCESS_QUERY_LIMITED_INFORMATION; no VM-read or write access.
            IntPtr handle = OpenProcess(0x1000, false, pid);
            if (handle == IntPtr.Zero)
                throw new Win32Exception(Marshal.GetLastWin32Error(),
                    "Cannot open target PID " + pid + " for limited image query.");
            try {
                uint length = 32768;
                var path = new StringBuilder((int)length);
                if (!QueryFullProcessImageNameW(handle, 0, path, ref length))
                    throw new Win32Exception(Marshal.GetLastWin32Error(),
                        "Cannot query target PID " + pid + " image path.");
                if (length == 0)
                    throw new InvalidOperationException("Target image path is empty.");
                return path.ToString();
            } finally { CloseHandle(handle); }
        }
    }
}
'@
    }
    [SfcM1.ProcessImageQuery]::Read($ProcessId)
}

function Wait-M1ProcessExit {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateRange(1, 2147483647)][int]$ProcessId,
        [Parameter(Mandatory)][ValidateRange(1, 3600)][int]$TimeoutSeconds
    )

    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        if (-not (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
            return [pscustomobject]@{ Outcome = 'exited'; ObservedAt = (Get-Date).ToString('o') }
        }
        Start-Sleep -Milliseconds 250
    } while ([DateTimeOffset]::UtcNow -lt $deadline)
    [pscustomobject]@{ Outcome = 'timeout-running'; ObservedAt = (Get-Date).ToString('o') }
}

Export-ModuleMember -Function Get-M1ProcessImagePath,Wait-M1ProcessExit
