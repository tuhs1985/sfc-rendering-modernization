# Read managed IL only; never load/execute the launcher or change registry/game.
param([string[]]$Methods=@('LaunchApplication','ApplySettings','GetFullPath'),[string]$DeclaringType='*')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$path=Join-Path $root 'Game Assets/SFCLauncher 2.1.0.22.exe'
if((Get-FileHash $path).Hash -ne '84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890'){throw 'Launcher baseline mismatch'}
if($Methods.Count -gt 8){throw 'Method scope cap'}
$ops=@{};foreach($field in [Reflection.Emit.OpCodes].GetFields()){if($field.FieldType -eq [Reflection.Emit.OpCode]){$o=$field.GetValue($null);$ops[[int]$o.Value -band 65535]=$o}}
$stream=[IO.File]::OpenRead($path)
try{
    $pe=[Reflection.PortableExecutable.PEReader]::new($stream)
    $md=[Reflection.Metadata.PEReaderExtensions]::GetMetadataReader($pe)
    function Resolve-Token([int]$token){
        $row=$token -band 0xffffff
        switch(($token -shr 24) -band 255){
            0x70 {return '"'+$md.GetUserString([Reflection.Metadata.Ecma335.MetadataTokens]::UserStringHandle($row))+'"'}
            0x06 {return $md.GetString($md.GetMethodDefinition([Reflection.Metadata.Ecma335.MetadataTokens]::MethodDefinitionHandle($row)).Name)}
            0x0A {return $md.GetString($md.GetMemberReference([Reflection.Metadata.Ecma335.MetadataTokens]::MemberReferenceHandle($row)).Name)}
            0x04 {return $md.GetString($md.GetFieldDefinition([Reflection.Metadata.Ecma335.MetadataTokens]::FieldDefinitionHandle($row)).Name)}
            default {return ('token0x{0:X8}' -f $token)}
        }
    }
    foreach($handle in $md.MethodDefinitions){
        $method=$md.GetMethodDefinition($handle);$name=$md.GetString($method.Name)
        if($name -notin $Methods -or -not $method.RelativeVirtualAddress){continue}
        $type=$md.GetTypeDefinition($method.GetDeclaringType());$typeName=$md.GetString($type.Name)
        if($typeName -notlike $DeclaringType){continue}
        [byte[]]$il=[Reflection.Metadata.PEReaderExtensions]::GetMethodBody($pe,$method.RelativeVirtualAddress).GetILBytes()
        if($il.Length -gt 4096){throw 'IL method size cap'}
        "METHOD $typeName.$name RVA $($method.RelativeVirtualAddress) bytes $($il.Length)"
        $i=0
        while($i -lt $il.Length){
            $offset=$i;$code=[int]$il[$i++];if($code -eq 254){$code=65024+[int]$il[$i++]}
            $op=$ops[[int]$code];if(-not $op){throw ('Unknown opcode0x{0:X4} at0x{1:X4}' -f $code,$offset)}
            $size=0;$value=''
            switch($op.OperandType.ToString()){
                InlineNone {}
                {$_ -in @('ShortInlineI','ShortInlineVar','ShortInlineBrTarget')} {$size=1;$value=$il[$i]}
                InlineVar {$size=2;$value=[BitConverter]::ToUInt16($il,$i)}
                InlineI8 {$size=8;$value=[BitConverter]::ToInt64($il,$i)}
                InlineR {$size=8;$value=[BitConverter]::ToDouble($il,$i)}
                ShortInlineR {$size=4;$value=[BitConverter]::ToSingle($il,$i)}
                InlineSwitch {$size=4+4*[BitConverter]::ToInt32($il,$i)}
                default {$size=4;$token=[BitConverter]::ToInt32($il,$i);$value=if($op.OperandType.ToString() -in @('InlineMethod','InlineField','InlineString','InlineTok','InlineType')){Resolve-Token $token}else{$token}}
            }
            ('IL_{0:X4} {1} {2}' -f $offset,$op.Name,$value);$i+=$size
        }
    }
}finally{$stream.Dispose()}
