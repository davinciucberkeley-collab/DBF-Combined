// Minimal type-library importer (no Windows SDK needed): TlbImp.exe <in.tlb> <out.dll> <namespace>
using System;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

class Sink : ITypeLibImporterNotifySink
{
    public void ReportEvent(ImporterEventKind k, int c, string m) { Console.WriteLine(m); }
    public Assembly ResolveRef(object typeLib) { return null; }
}
class TlbImp
{
    [DllImport("oleaut32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    static extern void LoadTypeLibEx(string file, int regKind, out ITypeLib lib);
    static void Main(string[] a)
    {
        ITypeLib lib; LoadTypeLibEx(a[0], 2, out lib);
        var conv = new TypeLibConverter();
        AssemblyBuilder ab = conv.ConvertTypeLibToAssembly(lib, System.IO.Path.GetFileName(a[1]), 0, new Sink(), null, null, a[2], null);
        ab.Save(System.IO.Path.GetFileName(a[1]));
        Console.WriteLine("wrote " + a[1]);
    }
}
