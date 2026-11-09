// Saves PNG views of the open/openable VTOL_Concept assembly. Usage: Snap.exe <asm path> <out dir>
using System;
using System.IO;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

class Snap
{
    static int Main(string[] a)
    {
        SldWorks sw = (SldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));
        int e = 0, w = 0;
        ModelDoc2 d = sw.OpenDoc6(a[0], (int)swDocumentTypes_e.swDocASSEMBLY, (int)swOpenDocOptions_e.swOpenDocOptions_Silent, "", ref e, ref w);
        if (d == null) { Console.WriteLine("open failed " + e); return 1; }
        sw.ActivateDoc3(d.GetTitle(), false, 0, ref e);
        string[][] views = { new[] { "*Isometric", "iso" }, new[] { "*Top", "top" }, new[] { "*Front", "side" }, new[] { "*Right", "front" } };
        foreach (var v in views)
        {
            d.ShowNamedView2(v[0], -1);
            d.ViewZoomtofit2();
            string p = Path.Combine(a[1], "VTOL_Concept_" + v[1] + ".png");
            bool ok = d.Extension.SaveAs(p, 0, 1, null, ref e, ref w);
            Console.WriteLine((ok ? "saved " : "FAILED ") + p);
        }
        d.ShowNamedView2("*Isometric", -1); d.ViewZoomtofit2();
        return 0;
    }
}
