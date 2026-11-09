// Checks that the Simulation and Flow Simulation add-ins load and expose their APIs.
using System;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.cosworks;

class Probe
{
    static void Main()
    {
        SldWorks sw = (SldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));
        int s = sw.LoadAddIn(@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll");
        Console.WriteLine("Simulation LoadAddIn = " + s);
        object cb = sw.GetAddInObject("SldWorks.Simulation");
        Console.WriteLine("Simulation addin object: " + (cb == null ? "null" : cb.GetType().Name));
        if (cb != null) { CosmosWorks cw = ((CwAddincallback)cb).CosmosWorks; Console.WriteLine("CosmosWorks: " + (cw == null ? "null" : "ok")); }
        object fo = sw.GetAddInObject("FloWorks.App");
        for (int i = 0; i < 20 && fo == null; i++) { System.Threading.Thread.Sleep(3000); fo = sw.GetAddInObject("FloWorks.App"); }
        Console.WriteLine("Flow addin object: " + (fo == null ? "null" : "ok"));
        if (fo != null)
        {
            dynamic app = fo;
            try { dynamic api = app.GetAPI(); Console.WriteLine("Flow AppApi ok; demo version = " + api.IsDemoVersion()); } catch (Exception e) { Console.WriteLine("GetAPI failed: " + e.Message); }
            try { object efd = app.GetNGPInterface(); Console.WriteLine("EFDApi (NGP) interface: " + (efd == null ? "null" : "ok")); } catch (Exception e) { Console.WriteLine("NGP failed: " + e.Message); }
        }
    }
}
